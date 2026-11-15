"""Pixel clock main loop: scene rotation, notification overlay, HTTP API, weather fetcher.

Run on the Pi:      sudo python3 -m pixelclock.app --config /etc/pixelclock.json
Preview anywhere:   python3 -m pixelclock.app --backend png --once out.png --scene clock
"""

import argparse
import io
import json
import os
import threading
import time
import urllib.request
from collections import deque
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

from . import scenes

DEFAULTS = {
    "rows": 32,
    "cols": 64,
    "hardware_mapping": "adafruit-hat",
    # Measured on the Pi 4 with a proper supply: a steady 360 Hz, no visible flicker
    "gpio_slowdown": 3,
    "pwm_bits": 8,
    "pwm_lsb_nanoseconds": 60,
    "limit_refresh_rate_hz": 360,
    "brightness_day": 20,
    "brightness_night": 12,
    "night_start": 22,
    "night_end": 7,
    "timezone": "America/New_York",
    "hour24": False,
    "units": "F",
    "port": 8765,
    "token": "",
    "latitude": None,
    "longitude": None,
    "rotation": [["clock", 25], ["indoor", 7], ["weather", 7], ["t3", 7], ["clock", 20], ["indoor", 7],
                 ["reminder", 6], ["system", 6]],
    "indoor_temp_offset_c": 0.0,  # subtract sensor self-heating, e.g. -3.0
    "co2_alert_ppm": 1200,
    "fps": 30,
}


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}
        self.queue = deque(maxlen=20)
        self.frame = scenes.blank()
        self.current = "clock"

    def merge(self, d):
        with self.lock:
            for k, v in d.items():
                if isinstance(v, dict):
                    v = dict(v)
                    v.setdefault("ts", time.time())
                self.data[k] = v

    def snapshot(self):
        with self.lock:
            return dict(self.data)

    def notify(self, n):
        n = dict(n)
        n["duration"] = scenes.notification_duration(n)
        with self.lock:
            # Collapse duplicates already waiting
            if any(q.get("title") == n.get("title") and q.get("text") == n.get("text") for q in self.queue):
                return
            self.queue.append(n)


def preview_png(frame, scale=10):
    """Render the frame the way the panel looks: round LEDs on black."""
    W, H = frame.size
    out = Image.new("RGB", (W * scale, H * scale), (8, 8, 10))
    d = ImageDraw.Draw(out)
    px = frame.load()
    r = scale * 0.42
    for y in range(H):
        for x in range(W):
            c = px[x, y]
            cx, cy = x * scale + scale / 2, y * scale + scale / 2
            if c == (0, 0, 0):
                c = (22, 22, 26)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return out


class MatrixBackend:
    def __init__(self, cfg):
        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        o = RGBMatrixOptions()
        o.rows = cfg["rows"]
        o.cols = cfg["cols"]
        o.hardware_mapping = cfg["hardware_mapping"]
        o.gpio_slowdown = cfg["gpio_slowdown"]
        o.brightness = cfg["brightness_day"]
        o.pwm_lsb_nanoseconds = cfg.get("pwm_lsb_nanoseconds", 130)
        o.pwm_bits = cfg.get("pwm_bits", 11)
        o.limit_refresh_rate_hz = cfg.get("limit_refresh_rate_hz", 0)
        o.drop_privileges = True
        if cfg.get("led_rgb_sequence"):
            o.led_rgb_sequence = cfg["led_rgb_sequence"]
        if cfg.get("panel_type"):
            o.panel_type = cfg["panel_type"]
        if cfg.get("row_address_type") is not None:
            o.row_address_type = cfg["row_address_type"]
        if cfg.get("multiplexing") is not None:
            o.multiplexing = cfg["multiplexing"]
        self.m = RGBMatrix(options=o)
        self.canvas = self.m.CreateFrameCanvas()

    def show(self, img, brightness):
        self.m.brightness = brightness
        self.canvas.brightness = brightness
        self.canvas.SetImage(img, 0, 0)
        self.canvas = self.m.SwapOnVSync(self.canvas)


class NullBackend:
    def show(self, img, brightness):
        pass


def brightness_for(cfg, now):
    h = now.hour
    ns, ne = cfg["night_start"], cfg["night_end"]
    night = h >= ns or h < ne
    return cfg["brightness_night"] if night else cfg["brightness_day"]


def run_loop(state, backend, cfg, stop):
    tz = ZoneInfo(cfg["timezone"])
    rot = cfg["rotation"]
    idx, scene_start = 0, time.time()
    notif, notif_start = None, 0.0
    t0 = time.time()
    period = 1.0 / cfg["fps"]
    while not stop.is_set():
        tick = time.time()
        now = datetime.now(tz)
        snap = state.snapshot()
        img = None
        if notif is None and state.queue:
            with state.lock:
                notif = state.queue.popleft()
            notif_start = tick
        if notif is not None:
            rel = tick - notif_start
            if rel > notif["duration"]:
                notif = None
                scene_start = tick  # restart the scene timer after a notification
            else:
                img = scenes.scene_notification(notif, rel)
                state.current = "notification"
        if img is None:
            name, dur = rot[idx % len(rot)]
            if tick - scene_start > dur:
                idx, scene_start = idx + 1, tick
                name, dur = rot[idx % len(rot)]
            fn = scenes.SCENES.get(name)
            img = fn(snap, now, tick - t0, cfg) if fn else None
            if img is None:  # scene has no data yet; skip it
                idx, scene_start = idx + 1, tick
                img = scenes.scene_clock(snap, now, tick - t0, cfg)
                name = "clock"
            state.current = name
        override = snap.get("brightness")
        b = int(override) if isinstance(override, (int, float)) else brightness_for(cfg, now)
        backend.show(img, b)
        state.frame = img
        # Full frame rate only while something scrolls; still screens redraw less often
        p = period if notif is not None else 1.0 / cfg.get("idle_fps", 12)
        stop.wait(max(0.0, p - (time.time() - tick)))


def geolocate():
    with urllib.request.urlopen("http://ip-api.com/json/?fields=lat,lon,city", timeout=10) as r:
        d = json.load(r)
    return d["lat"], d["lon"], d.get("city", "")


def weather_loop(state, cfg, stop):
    lat, lon = cfg.get("latitude"), cfg.get("longitude")
    while not stop.is_set():
        try:
            if lat is None or lon is None:
                lat, lon, city = geolocate()
                state.merge({"location": {"lat": round(lat, 2), "lon": round(lon, 2), "city": city}})
            unit = "fahrenheit" if cfg["units"] == "F" else "celsius"
            url = ("https://api.open-meteo.com/v1/forecast?latitude=%.2f&longitude=%.2f"
                   "&current=temperature_2m,weather_code,is_day&daily=temperature_2m_max,temperature_2m_min"
                   "&temperature_unit=%s&timezone=auto&forecast_days=1") % (lat, lon, unit)
            with urllib.request.urlopen(url, timeout=15) as r:
                d = json.load(r)
            cur = d["current"]
            state.merge({"weather": {
                "temp": cur["temperature_2m"], "code": cur["weather_code"], "is_day": cur["is_day"],
                "hi": d["daily"]["temperature_2m_max"][0], "lo": d["daily"]["temperature_2m_min"][0],
            }})
            stop.wait(900)
        except Exception as e:  # network hiccup: try again soon
            state.merge({"weather_error": {"error": str(e)[:200]}})
            stop.wait(120)


def sensor_loop(state, cfg, stop, scd, aht):
    """Read the SCD41 and AHT sensors every 5 s; pop up once when CO2 crosses the alert level."""
    off = cfg.get("indoor_temp_offset_c", 0.0)
    alert = cfg.get("co2_alert_ppm", 1200)
    alerted = False
    last = {}
    while not stop.is_set():
        try:
            if scd:
                r = scd.read()
                if r:
                    last["co2"] = r[0]
                    last.setdefault("temp", r[1] + off)
                    last.setdefault("hum", r[2])
            if aht:
                t, h = aht.read()
                last["temp"], last["hum"] = t + off, h
            if last:
                state.merge({"indoor": dict(last)})
            co2 = last.get("co2")
            if co2 is not None:
                if co2 >= alert and not alerted:
                    alerted = True
                    state.notify({"icon": "window", "title": "Air is stale", "text": f"CO2 {co2} ppm. Open a window!",
                                  "color": [255, 170, 0], "duration": 10})
                elif co2 < alert - 150:
                    alerted = False
        except Exception as e:
            state.merge({"sensor_error": {"error": str(e)[:200]}})
        stop.wait(5)


def make_handler(state, cfg):
    token = cfg.get("token") or ""

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json"):
            if isinstance(body, (dict, list)):
                body = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path.startswith("/frame.png"):
                buf = io.BytesIO()
                preview_png(state.frame).save(buf, "PNG")
                return self._send(200, buf.getvalue(), "image/png")
            if self.path.startswith("/state"):
                s = state.snapshot()
                s["current"] = state.current
                s["queued"] = len(state.queue)
                return self._send(200, s)
            if self.path in ("/", "/index.html"):
                html = (b"<!doctype html><meta name=viewport content='width=device-width'>"
                        b"<title>Pixel clock</title><body style='margin:0;background:#111'>"
                        b"<img id=f style='width:100%;image-rendering:pixelated' src='/frame.png'>"
                        b"<script>setInterval(()=>{f.src='/frame.png?'+Date.now()},250)</script>")
                return self._send(200, html, "text/html")
            self._send(404, {"error": "not found"})

        def do_POST(self):
            if token and self.headers.get("X-Token") != token:
                return self._send(401, {"error": "bad token"})
            n = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(n) or b"{}")
            except json.JSONDecodeError:
                return self._send(400, {"error": "bad json"})
            if self.path == "/notify":
                state.notify(body)
                return self._send(200, {"ok": True, "queued": len(state.queue)})
            if self.path == "/state":
                state.merge(body)
                return self._send(200, {"ok": True})
            self._send(404, {"error": "not found"})

    return H


def load_cfg(path):
    cfg = dict(DEFAULTS)
    if path and os.path.exists(path):
        with open(path) as f:
            cfg.update(json.load(f))
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="/etc/pixelclock.json")
    ap.add_argument("--backend", choices=["matrix", "null"], default="matrix")
    ap.add_argument("--no-weather", action="store_true")
    ap.add_argument("--no-sensors", action="store_true")
    args = ap.parse_args()
    cfg = load_cfg(args.config)
    state = State()
    stop = threading.Event()
    # Open I2C before the matrix library drops root privileges; the open handle keeps working after
    scd = aht = None
    if not args.no_sensors:
        from .sensors import open_sensors
        try:
            _bus, scd, aht = open_sensors()
        except OSError:
            pass
    backend = MatrixBackend(cfg) if args.backend == "matrix" else NullBackend()
    if scd or aht:
        threading.Thread(target=sensor_loop, args=(state, cfg, stop, scd, aht), daemon=True).start()
    srv = ThreadingHTTPServer(("0.0.0.0", cfg["port"]), make_handler(state, cfg))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    if not args.no_weather:
        threading.Thread(target=weather_loop, args=(state, cfg, stop), daemon=True).start()
    state.notify({"icon": "heart", "title": "Pixel clock", "text": "Hello!", "color": [255, 60, 170]})
    try:
        run_loop(state, backend, cfg, stop)
    except KeyboardInterrupt:
        stop.set()


if __name__ == "__main__":
    main()
