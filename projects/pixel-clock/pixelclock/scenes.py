"""Scenes for a 64x32 panel. Each returns a PIL RGB image; pure functions of state + time."""

import math
import time
from datetime import datetime

from PIL import Image

from .font import MED, SMALL, draw_text, text_width
from .icons import PALETTE, draw_icon

W, H = 64, 32
WHITE = (235, 235, 235)
DIM = (70, 70, 80)
AMBER = (255, 170, 0)
CYAN = (0, 200, 255)
GREEN = (0, 230, 0)
RED = (255, 50, 50)
PURPLE = (190, 70, 255)


def blank():
    return Image.new("RGB", (W, H), (0, 0, 0))


def draw_big(img, x, y, text, color, sx=2, sy=3, spacing=1):
    """MED font stretched sx by sy: 10x21 digits at the default size."""
    px = img.load()
    for ch in text:
        g = MED.get(ch) or MED["?"]
        for ry, row in enumerate(g):
            for rx, c in enumerate(row):
                if c != "#":
                    continue
                for yy in range(sy):
                    for xx in range(sx):
                        X, Y = x + rx * sx + xx, y + ry * sy + yy
                        if 0 <= X < W and 0 <= Y < H:
                            px[X, Y] = color
        x += (len(g[0]) + spacing) * sx
    return x


def big_width(text, sx=2, spacing=1):
    return sum((len((MED.get(c) or MED["?"])[0]) + spacing) * sx for c in text) - spacing * sx


def centered_small(img, y, text, color):
    draw_text(img, (W - text_width(text, SMALL)) // 2, y, text, color, font=SMALL)


def weekday_bar(img, now, y=31):
    # Seven dashes, Monday first; today's is lit, like the reference clock.
    for i in range(7):
        x0 = 2 + i * 9
        col = WHITE if i == now.weekday() else (45, 45, 50)
        for x in range(x0, x0 + 7):
            img.putpixel((x, y), col)


def scene_clock(state, now, t, cfg):
    img = blank()
    h = now.hour if cfg.get("hour24") else (now.hour % 12 or 12)
    hh = f"{h:d}" if not cfg.get("hour24") else f"{h:02d}"
    mm = f"{now.minute:02d}"
    color = tuple(cfg.get("clock_color", WHITE))
    wh = big_width(hh)
    total = wh + 6 + big_width(mm)
    x0 = (W - total) // 2 - 3
    draw_big(img, x0, 1, hh, color)
    # Blinking colon
    cx = x0 + wh + 2
    if now.second % 2 == 0 or not cfg.get("blink_colon", True):
        for yy in (7, 8, 14, 15):
            img.putpixel((cx, yy), color)
            img.putpixel((cx + 1, yy), color)
    draw_big(img, cx + 4, 1, mm, color)
    # Seconds, small, top right column
    draw_text(img, 57, 1, f"{now.second:02d}"[0], DIM, font=SMALL)
    draw_text(img, 57, 7, f"{now.second:02d}"[1], DIM, font=SMALL)
    # Bottom line: date left, temperature right
    date = now.strftime("%a %b %d").upper().replace(" 0", " ")
    draw_text(img, 1, 24, date, (160, 160, 170), font=SMALL)
    wx = state.get("weather") or {}
    if "temp" in wx:
        tt = f"{round(wx['temp'])}°"
        draw_text(img, W - text_width(tt, SMALL) - 1, 24, tt, AMBER, font=SMALL)
    # T3 attention dot: amber if something waits on you, cyan pulse while agents work
    t3 = state.get("t3") or {}
    if t3.get("waiting"):
        if int(t * 2) % 2 == 0:
            img.putpixel((63, 0), AMBER)
    elif t3.get("running"):
        b = int(80 + 80 * math.sin(t * 3))
        img.putpixel((63, 0), (0, b, b))
    weekday_bar(img, now)
    return img


def icon_value(icon, value, unit, label, value_color=WHITE, label_color=(160, 160, 170), anim_t=0.0):
    """The reference clock's main layout: big icon left, big number right, unit and label small."""
    img = blank()
    bob = 0
    draw_icon(img, 1, 4 + bob, icon, scale=3)
    vx = 28
    vw = big_width(value, sx=2)
    if vx + vw > 63:
        # Fall back to a narrower number if it would not fit
        draw_big(img, vx, 3, value, value_color, sx=1, sy=3)
        end = vx + big_width(value, sx=1)
    else:
        end = draw_big(img, vx, 3, value, value_color, sx=2, sy=2)
    if unit:
        draw_text(img, min(end + 1, 63 - text_width(unit, SMALL)), 12, unit, value_color, font=SMALL)
    if label:
        lw = text_width(label, SMALL)
        lx = max(28, min(63 - lw, 28))
        if lx + lw > 64:
            lx = 64 - lw
        draw_text(img, lx, 20, label, label_color, font=SMALL)
    return img


WMO = {
    0: ("sun", "CLEAR"), 1: ("partly", "MOSTLY CLR"), 2: ("partly", "PARTLY"), 3: ("cloud", "CLOUDY"),
    45: ("fog", "FOG"), 48: ("fog", "FOG"),
    51: ("rain", "DRIZZLE"), 53: ("rain", "DRIZZLE"), 55: ("rain", "DRIZZLE"),
    56: ("rain", "ICY DRZL"), 57: ("rain", "ICY DRZL"),
    61: ("rain", "RAIN"), 63: ("rain", "RAIN"), 65: ("rain", "HEAVY RAIN"),
    66: ("rain", "ICY RAIN"), 67: ("rain", "ICY RAIN"),
    71: ("snow", "SNOW"), 73: ("snow", "SNOW"), 75: ("snow", "HEAVY SNOW"), 77: ("snow", "SNOW"),
    80: ("rain", "SHOWERS"), 81: ("rain", "SHOWERS"), 82: ("rain", "DOWNPOUR"),
    85: ("snow", "SNOW SHWR"), 86: ("snow", "SNOW SHWR"),
    95: ("storm", "STORM"), 96: ("storm", "STORM"), 99: ("storm", "STORM"),
}


def scene_weather(state, now, t, cfg):
    wx = state.get("weather") or {}
    if "temp" not in wx:
        return None
    icon, word = WMO.get(wx.get("code", 0), ("cloud", ""))
    if icon == "sun" and not wx.get("is_day", 1):
        icon, word = "moon", "CLEAR"
    img = icon_value(icon, f"{round(wx['temp'])}", "°F" if cfg.get("units", "F") == "F" else "°C",
                     word, value_color=AMBER)
    if "hi" in wx:
        s = f"H{round(wx['hi'])} L{round(wx['lo'])}"
        draw_text(img, 28, 26, s, DIM, font=SMALL)
    _weather_fx(img, icon, t)
    return img


def _weather_fx(img, icon, t):
    """Small falling drops or flakes under the icon area for rain and snow."""
    if icon not in ("rain", "snow"):
        return
    col = (40, 110, 255) if icon == "rain" else (200, 200, 220)
    speed = 18 if icon == "rain" else 6
    for i in range(6):
        x = 2 + (i * 5) % 22
        y = int(28 + ((t * speed + i * 7) % 4))
        if 0 <= y < H:
            img.putpixel((x, y), col)


def scene_t3(state, now, t, cfg):
    t3 = state.get("t3")
    if not t3 or time.time() - t3.get("ts", 0) > 300:
        return None
    if t3.get("waiting"):
        img = icon_value("bell", str(t3["waiting"]), "", "NEED YOU", value_color=AMBER, label_color=AMBER)
        title = (t3.get("waiting_titles") or [""])[0]
        if title:
            _ticker(img, 26, title.upper(), DIM, t, x0=28)
        return img
    running = t3.get("running", 0)
    img = icon_value("robot", str(running), "", "AGENTS" if running != 1 else "AGENT",
                     value_color=CYAN if running else DIM)
    done = t3.get("done_today", 0)
    draw_text(img, 28, 26, f"DONE {done}", GREEN if done else DIM, font=SMALL)
    # Activity bar: one lit pixel per running agent, pulsing
    for i in range(min(running, 24)):
        b = int(120 + 120 * math.sin(t * 4 + i))
        img.putpixel((1 + i, 30), (0, b, b))
    return img


def scene_system(state, now, t, cfg):
    s = state.get("system")
    if not s or time.time() - s.get("ts", 0) > 300:
        return None
    img = blank()
    draw_icon(img, 1, 1, "cpu", scale=2)
    draw_text(img, 20, 1, "DESKTOP", DIM, font=SMALL)
    rows = [("CPU", s.get("cpu", 0), CYAN), ("GPU", s.get("gpu", 0), GREEN), ("MEM", s.get("mem", 0), PURPLE)]
    for i, (name, val, col) in enumerate(rows):
        y = 8 + i * 7
        draw_text(img, 20, y, name, (150, 150, 160), font=SMALL)
        n = int(max(0, min(100, val)) * 28 / 100)
        for x in range(34, 62):
            c = col if x - 34 < n else (25, 25, 30)
            for yy in range(y, y + 5):
                img.putpixel((x, yy), c)
    if "gpu_temp" in s:
        draw_text(img, 1, 20, f"{s['gpu_temp']}°", AMBER, font=SMALL)
        draw_text(img, 1, 26, "GPU", DIM, font=SMALL)
    return img


def scene_reminder(state, now, t, cfg):
    r = state.get("reminder")
    if not r or not r.get("when"):
        return None
    img = blank()
    draw_icon(img, 1, 4, "alarm", scale=3)
    draw_text(img, 28, 2, "NEXT UP", (160, 160, 170), font=SMALL)
    x = draw_text(img, 28, 9, r["when"], WHITE, font=MED)
    if r.get("ampm"):
        draw_text(img, x + 1, 11, r["ampm"], WHITE, font=SMALL)
    if r.get("day"):
        draw_text(img, 28, 18, r["day"].upper(), AMBER, font=SMALL)
    if r.get("text"):
        _ticker(img, 26, r["text"].upper(), DIM, t, x0=28)
    return img


def co2_color(ppm):
    if ppm < 800:
        return GREEN
    if ppm < 1200:
        return AMBER
    return RED


def scene_indoor(state, now, t, cfg):
    s = state.get("indoor")
    if not s or time.time() - s.get("ts", 0) > 120:
        return None
    img = blank()
    co2 = s.get("co2")
    if co2 is not None:
        col = co2_color(co2)
        draw_icon(img, 1, 4, "leaf" if co2 < 1200 else "window", scale=3)
        v = str(int(co2))
        if len(v) <= 3:
            draw_big(img, 28, 1, v, col, sx=2, sy=2)
        else:  # 4 digits: narrower
            draw_big(img, 28, 1, v, col, sx=1, sy=2)
        draw_text(img, 28, 17, "CO2", (160, 160, 170), font=SMALL)
        draw_text(img, 50, 17, "PPM", col, font=SMALL)
        # Level bar: 400 to 2000 ppm
        n = int(max(0, min(1, (co2 - 400) / 1600)) * 35)
        for x in range(28, 63):
            img.putpixel((x, 23), col if x - 28 < n else (30, 30, 35))
    else:
        draw_icon(img, 1, 4, "leaf", scale=3)
    if s.get("temp") is not None:
        units = cfg.get("units", "F")
        tt = s["temp"] if units == "C" else s["temp"] * 9 / 5 + 32
        draw_text(img, 28, 26, f"{round(tt)}°", AMBER, font=SMALL)
    if s.get("hum") is not None:
        draw_text(img, 46, 26, f"{round(s['hum'])}%", CYAN, font=SMALL)
    return img


def _ticker(img, y, text, color, t, x0=0, speed=14):
    """Scroll text within [x0, 64) on row y (SMALL font)."""
    tw = text_width(text, SMALL)
    span = W - x0
    if tw <= span:
        draw_text(img, x0, y, text, color, font=SMALL)
        return
    strip = Image.new("RGB", (tw + span, 5))
    draw_text(strip, 0, 0, text, color, font=SMALL)
    off = int(t * speed) % (tw + span // 2)
    region = strip.crop((off, 0, off + span, 5))
    for yy in range(5):
        for xx in range(span):
            p = region.getpixel((xx, yy))
            if p != (0, 0, 0):
                img.putpixel((x0 + xx, y + yy), p)


def scene_notification(n, t_rel):
    """A notification: colored frame slides in, icon left, title + body scroll in MED font."""
    img = blank()
    color = tuple(n.get("color") or PALETTE.get("P"))
    slide = min(1.0, t_rel / 0.35)
    off = int((1 - slide) * H)
    # Frame
    for x in range(W):
        for y in (0 + off, H - 1 + off):
            if 0 <= y < H:
                img.putpixel((x, y), color)
    for y in range(off, min(H, H + off)):
        img.putpixel((0, y), color)
        img.putpixel((W - 1, y), color)
    draw_icon(img, 3, 4 + off, n.get("icon", "chat"), scale=3)
    title = (n.get("title") or "").upper()
    body = n.get("text") or ""
    region_x = 30
    if title:
        tw = text_width(title, SMALL)
        if tw <= W - region_x - 2:
            draw_text(img, region_x, 3 + off, title, color, font=SMALL)
        else:
            strip = Image.new("RGB", (tw + 40, 5))
            draw_text(strip, 0, 0, title, color, font=SMALL)
            o = int(max(0, t_rel - 1) * 12) % (tw + 20)
            _blit(img, strip.crop((o, 0, o + W - region_x - 2, 5)), region_x, 3 + off)
    if body:
        bw = text_width(body, MED)
        span = W - region_x - 2
        if bw <= span:
            draw_text(img, region_x, 13 + off, body, WHITE, font=MED)
        else:
            strip = Image.new("RGB", (bw + span * 2, 7))
            draw_text(strip, span, 0, body, WHITE, font=MED)
            o = int(max(0, t_rel - 0.5) * 22) % (bw + span)
            _blit(img, strip.crop((o, 0, o + span, 7)), region_x, 13 + off)
    # Progress line showing time left
    dur = n.get("duration", 8)
    left = max(0.0, 1 - t_rel / dur)
    for x in range(2, 2 + int((W - 4) * left)):
        img.putpixel((x, H - 3), tuple(c // 3 for c in color))
    return img


def _blit(img, region, x, y):
    for yy in range(region.height):
        for xx in range(region.width):
            p = region.getpixel((xx, yy))
            if p != (0, 0, 0) and 0 <= x + xx < W and 0 <= y + yy < H:
                img.putpixel((x + xx, y + yy), p)


def notification_duration(n):
    body = n.get("text") or ""
    title = n.get("title") or ""
    span = W - 32
    need = max(text_width(body, MED) + span, 0) / 22 + 1.5
    need = max(need, text_width(title, SMALL) / 12 + 2)
    return max(float(n.get("duration") or 0), min(30.0, max(5.0, need * 1.6)))


SCENES = {
    "clock": scene_clock,
    "weather": scene_weather,
    "t3": scene_t3,
    "reminder": scene_reminder,
    "indoor": scene_indoor,
    "system": scene_system,
}
