"""Pico W sensor box: SCD41, VL53L1X and MAX30101 on a Pico Breakout Garden Base,
readings scrolled on an LTP305 green matrix and served over Wi-Fi as JSON.

GET /data.json  latest readings (the desk service polls this)
GET /           the same readings as a small page

Every part is optional: a missing breakout is skipped and looked for again every 30 s.
A hardware watchdog restarts the board if the program ever freezes. Press Ctrl-C over
USB (or use tools/deploy.sh) to get a REPL; the watchdog then stays fed until reset.
"""
import gc
import json
import time

import machine
import network
import rp2
import uasyncio as asyncio
from pimoroni_i2c import PimoroniI2C

import font5x7

VERSION = 1
CFG = {"ssid": "", "password": "", "hostname": "pico-sensors", "name": "", "country": "US",
       "brightness": 0.5, "night_brightness": 0.1, "night_start": 22, "night_end": 7,
       "temp_offset_f": 0.0, "co2_alert_ppm": 1200, "co2_buzz": True}
try:
    with open("config.json") as f:
        CFG.update(json.load(f))
except (OSError, ValueError):
    pass

# ---------------------------------------------------------------- watchdog
_beat = time.ticks_ms()
_dev = False                       # set after Ctrl-C so the REPL is not reset under you
_wdt = machine.WDT(timeout=8000)


def _feed(_t):
    if _dev or time.ticks_diff(time.ticks_ms(), _beat) < 6000:
        _wdt.feed()


_wdt_timer = machine.Timer(period=1000, mode=machine.Timer.PERIODIC, callback=_feed)


def heartbeat():
    global _beat
    _beat = time.ticks_ms()


# ---------------------------------------------------------------- state
state = {
    "device": "pico-sensors", "v": VERSION, "name": CFG["name"], "mac": None,
    "uptime_s": 0, "ip": None, "rssi": None,
    "co2_ppm": None, "temp_c": None, "temp_f": None, "humidity_pct": None,
    "distance_mm": None, "finger": False, "bpm": None,
    "parts": {"scd41": False, "vl53l1x": False, "max30101": False, "matrix": False, "haptic": False},
}


class Haptic:
    """DRV2605L haptic driver (Pimoroni Haptic Bzzz), open loop so it needs no calibration."""
    ADDR = 0x5A

    def __init__(self, i2c):
        self.i2c = i2c
        if self._r(0x00) >> 5 != 7:
            raise OSError("DRV2605L not found")
        self._w(0x01, 0x00)                       # out of standby, internal trigger
        self._w(0x1A, 0xB6)                       # linear resonant actuator
        self._w(0x1D, self._r(0x1D) | 0x01)       # open loop
        self._w(0x03, 6)                          # LRA effect library
        self._w(0x01, 0x40)                       # standby until needed

    def _w(self, reg, v):
        self.i2c.writeto_mem(self.ADDR, reg, bytes([v]))

    def _r(self, reg):
        return self.i2c.readfrom_mem(self.ADDR, reg, 1)[0]

    async def buzz(self, times=3, effect=47):
        self._w(0x01, 0x00)
        for _ in range(times):
            self._w(0x04, effect)
            self._w(0x05, 0)
            self._w(0x0C, 1)                      # GO
            for _ in range(100):
                await asyncio.sleep_ms(20)
                if not self._r(0x0C) & 1:
                    break
            await asyncio.sleep_ms(300)
        self._w(0x01, 0x40)
i2c = PimoroniI2C(sda=4, scl=5, baudrate=100000)
parts = {}


def try_init():
    """Bring up whatever breakouts are present and not yet running."""
    found = i2c.scan()
    if "matrix" not in parts and 0x61 in found:
        try:
            from breakout_dotmatrix import BreakoutDotMatrix
            parts["matrix"] = BreakoutDotMatrix(i2c)
        except Exception as e:      # noqa
            print("matrix:", e)
    if "scd41" not in parts and 0x62 in found:
        try:
            import breakout_scd41 as scd
            scd.init(i2c)
            try:
                scd.start()
            except Exception:       # already measuring after a soft reset
                pass
            parts["scd41"] = scd
        except Exception as e:      # noqa
            print("scd41:", e)
    if "vl53l1x" not in parts and 0x29 in found:
        try:
            from vl53l1x import VL53L1X
            parts["vl53l1x"] = VL53L1X(i2c)
        except Exception as e:      # noqa
            print("vl53l1x:", e)
    if "max30101" not in parts and 0x57 in found:
        try:
            from max30101 import MAX30101
            parts["max30101"] = MAX30101(i2c)
        except Exception as e:      # noqa
            print("max30101:", e)
    if "haptic" not in parts and Haptic.ADDR in found:
        try:
            parts["haptic"] = Haptic(i2c)
        except Exception as e:      # noqa
            print("haptic:", e)
    for k in state["parts"]:
        state["parts"][k] = k in parts


def drop(name, e):
    print(name, "failed:", e)
    parts.pop(name, None)
    state["parts"][name] = False


# ---------------------------------------------------------------- Eastern time for night dimming
def eastern_hour():
    t = time.time()
    y = time.localtime(t)[0]
    if y < 2024:                    # clock not set yet
        return 12

    def nth_sunday(month, n):       # UTC timestamp of 2 AM local on the nth Sunday
        first = time.mktime((y, month, 1, 0, 0, 0, 0, 0))
        wd = time.localtime(first)[6]            # Monday = 0
        day = 1 + (6 - wd) % 7 + 7 * (n - 1)
        return time.mktime((y, month, day, 2, 0, 0, 0, 0))

    dst = nth_sunday(3, 2) + 5 * 3600 <= t < nth_sunday(11, 1) + 4 * 3600
    return time.localtime(t - (4 if dst else 5) * 3600)[3]


# ---------------------------------------------------------------- tasks
async def wifi_task():
    rp2.country(CFG["country"])
    network.hostname(CFG["hostname"])
    w = network.WLAN(network.STA_IF)
    w.active(True)
    w.config(pm=0xa11140)            # no Wi-Fi power saving: keeps the HTTP server snappy
    state["mac"] = ":".join("%02x" % b for b in w.config("mac"))
    synced = False
    while True:
        if not w.isconnected() and CFG["ssid"]:
            state["ip"] = None
            w.connect(CFG["ssid"], CFG["password"])
            for _ in range(40):
                if w.isconnected() or w.status() < 0:
                    break
                await asyncio.sleep_ms(500)
        if w.isconnected():
            state["ip"] = w.ifconfig()[0]
            state["rssi"] = w.status("rssi")
            if not synced:
                try:
                    import ntptime
                    ntptime.settime()
                    synced = True
                except Exception:   # noqa
                    pass
        await asyncio.sleep(15)


async def sensor_task():
    last_scan = time.ticks_add(time.ticks_ms(), -30000)
    up_ms, prev = 0, time.ticks_ms()
    while True:
        heartbeat()
        now = time.ticks_ms()
        up_ms += time.ticks_diff(now, prev)
        prev = now
        if time.ticks_diff(now, last_scan) > 30000 and len(parts) < 5:
            last_scan = now
            try:
                try_init()
            except Exception as e:  # noqa
                print("scan:", e)
        if "scd41" in parts:
            try:
                scd = parts["scd41"]
                if scd.ready():
                    co2, tc, rh = scd.measure()
                    state["co2_ppm"] = round(co2)
                    state["temp_c"] = round(tc, 2)
                    state["temp_f"] = round(tc * 9 / 5 + 32 + CFG["temp_offset_f"], 1)
                    state["humidity_pct"] = round(rh, 1)
            except Exception as e:  # noqa
                drop("scd41", e)
        if "vl53l1x" in parts:
            try:
                tof = parts["vl53l1x"]
                if tof.ready():
                    state["distance_mm"] = tof.read()
            except Exception as e:  # noqa
                drop("vl53l1x", e)
        if "max30101" in parts:
            try:
                mx = parts["max30101"]
                mx.update()
                state["finger"] = mx.finger()
                state["bpm"] = mx.bpm()
            except Exception as e:  # noqa
                drop("max30101", e)
        state["uptime_s"] = up_ms // 1000
        await asyncio.sleep_ms(40)


def is_night():
    h = eastern_hour()
    return h >= CFG["night_start"] or h < CFG["night_end"]


def co2_high():
    return state["co2_ppm"] is not None and state["co2_ppm"] > CFG["co2_alert_ppm"]


async def buzz():
    h = parts.get("haptic")
    if h is None:
        return False
    try:
        await h.buzz()
        return True
    except Exception as e:          # noqa
        drop("haptic", e)
        return False


async def alert_task():
    """Buzz when CO2 crosses the alert level: at most every 30 minutes, never at night."""
    last = None
    while True:
        await asyncio.sleep(10)
        if co2_high() and CFG["co2_buzz"] and not is_night():
            now = time.ticks_ms()
            if last is None or time.ticks_diff(now, last) > 30 * 60 * 1000:
                if await buzz():
                    last = now


def ticker_text():
    bits = ["OPEN WINDOW"] if co2_high() else []
    if state["co2_ppm"] is not None:
        bits.append("CO2 %d" % state["co2_ppm"])
    if state["temp_f"] is not None:
        bits.append("%.1f%sF" % (state["temp_f"], font5x7.DEGREE))
    if state["humidity_pct"] is not None:
        bits.append("%d%%" % round(state["humidity_pct"]))
    if state["distance_mm"] is not None:
        bits.append("%dcm" % round(state["distance_mm"] / 10))
    if not bits:
        bits.append(state["ip"] or "no wifi")
    return "   ".join(bits) + "   "


def columns(text):
    """Text as a list of pixel columns, glyphs trimmed to their width plus 1 px gap."""
    out = []
    for ch in text:
        if ch == " ":
            out += [0, 0]
            continue
        g = [c for c in font5x7.glyph(ch)]
        while g and g[0] == 0:
            g.pop(0)
        while g and g[-1] == 0:
            g.pop()
        out += g + [0]
    return out


def draw(m, cols, offset):
    m.clear()
    for x in range(10):
        i = offset + x
        if 0 <= i < len(cols):
            c = cols[i]
            for y in range(7):
                if c >> y & 1:
                    m.set_pixel(x, y, True)


async def display_task():
    offset, cols = 0, []
    beat_on = False
    while True:
        m = parts.get("matrix")
        if m is None:
            await asyncio.sleep_ms(500)
            continue
        try:
            m.set_brightness(CFG["night_brightness"] if is_night() else CFG["brightness"])
            if state["finger"]:
                # heart rate mode: the matrix's two 5x7 digits; the right decimal point
                # flashes, the left one means "plus 100". A pulsing heart while it measures.
                bpm = state["bpm"]
                beat_on = not beat_on
                if bpm:
                    s = "%02d" % (bpm % 100)
                    m.clear()
                    m.set_character(0, ord(s[0]))
                    m.set_character(5, ord(s[1]))
                    m.set_decimal(left=bpm >= 100, right=beat_on)
                else:
                    draw(m, [0, 0] + columns(font5x7.HEART) if beat_on else [], 0)
                m.show()
                offset, cols = 0, []
                await asyncio.sleep_ms(300)
                continue
            if offset == 0 or not cols:
                cols = [0] * 10 + columns(ticker_text())
            draw(m, cols, offset)
            m.show()
            offset = (offset + 1) % len(cols)
        except Exception as e:      # noqa
            drop("matrix", e)
        await asyncio.sleep_ms(90)


def payload():
    return json.dumps(state)


PAGE = """<!doctype html><meta name=viewport content="width=device-width"><title>Pico sensors</title>
<body style="font:16px system-ui;margin:24px;color:#0b0b0b;background:#fcfcfb"><h2>Pico sensors</h2><pre>%s</pre>
<p>Raw JSON: <a href="/data.json">/data.json</a></p>"""


async def http(reader, writer):
    try:
        line = await reader.readline()
        while True:                 # skip the headers
            h = await reader.readline()
            if not h or h == b"\r\n":
                break
        path = line.split(b" ")[1] if b" " in line else b"/"
        if path.startswith(b"/data.json"):
            body, ctype = payload(), "application/json"
        elif path.startswith(b"/scan"):
            try:
                found = ["0x%02x" % a for a in i2c.scan()]
            except Exception as e:  # noqa
                found = str(e)
            body, ctype = json.dumps({"i2c": found, "parts": state["parts"]}), "application/json"
        elif path.startswith(b"/buzz"):
            ok = "haptic" in parts
            if ok:
                asyncio.create_task(buzz())
            body, ctype = json.dumps({"buzz": ok}), "application/json"
        elif path == b"/":
            body, ctype = PAGE % json.dumps(state).replace(", ", ",\n "), "text/html"
        else:
            body, ctype = '{"error": "not found"}', "application/json"
        writer.write("HTTP/1.0 200 OK\r\nContent-Type: %s\r\nAccess-Control-Allow-Origin: *\r\n"
                     "Content-Length: %d\r\nConnection: close\r\n\r\n" % (ctype, len(body)))
        writer.write(body)
        await writer.drain()
    except Exception as e:          # noqa
        print("http:", e)
    finally:
        writer.close()
        await writer.wait_closed()
        gc.collect()


async def main():
    asyncio.create_task(wifi_task())
    asyncio.create_task(sensor_task())
    asyncio.create_task(display_task())
    asyncio.create_task(alert_task())
    await asyncio.start_server(http, "0.0.0.0", 80)
    while True:
        await asyncio.sleep(60)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    _dev = True                     # keep the watchdog fed while you work in the REPL
    print("stopped; watchdog held off until the next reset")
