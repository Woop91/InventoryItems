"""Render every scene with sample data into one contact sheet PNG (no Pi needed).

python3 projects/pixel-clock/tools/preview.py OUT.png
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw  # noqa: E402

from pixelclock import scenes  # noqa: E402
from pixelclock.app import DEFAULTS, preview_png  # noqa: E402

now = datetime.now(ZoneInfo("America/New_York"))
ts = time.time()
state = {
    "weather": {"temp": 47.3, "code": 61, "is_day": 0, "hi": 52, "lo": 38, "ts": ts},
    "t3": {"running": 7, "waiting": 0, "done_today": 23, "ts": ts},
    "system": {"cpu": 42, "gpu": 77, "mem": 61, "gpu_temp": 64, "ts": ts},
    "reminder": {"when": "9:00", "ampm": "PM", "text": "Check the release plan", "ts": ts},
    "indoor": {"co2": 779, "temp": 22.4, "hum": 41, "ts": ts},
}
waiting = dict(state, t3={"running": 5, "waiting": 2, "done_today": 9, "ts": ts,
                         "waiting_titles": ["Sunday release plan"]})
cfg = dict(DEFAULTS)
frames = [
    ("clock", scenes.scene_clock(state, now, 0, cfg)),
    ("indoor air", scenes.scene_indoor(state, now, 0, cfg)),
    ("indoor air, stale", scenes.scene_indoor(dict(state, indoor={"co2": 1460, "temp": 23.5, "hum": 48, "ts": ts}),
                                              now, 0, cfg)),
    ("weather", scenes.scene_weather(state, now, 0.3, cfg)),
    ("t3 agents", scenes.scene_t3(state, now, 0.2, cfg)),
    ("t3 needs you", scenes.scene_t3(waiting, now, 0.2, cfg)),
    ("reminder", scenes.scene_reminder(state, now, 0, cfg)),
    ("system", scenes.scene_system(state, now, 0, cfg)),
    ("notification", scenes.scene_notification(
        {"icon": "check", "title": "T3 done", "text": "Inventory PR merged", "color": [40, 220, 80],
         "duration": 8}, 1.2)),
    ("desktop notice", scenes.scene_notification(
        {"icon": "chat", "title": "Firefox", "text": "Download complete", "color": [190, 70, 255],
         "duration": 8}, 3.0)),
]
scale = 8
pw, ph = 64 * scale, 32 * scale
cols = 2
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (pw + 20) + 20, rows * (ph + 40) + 20), (245, 245, 247))
d = ImageDraw.Draw(sheet)
for i, (name, f) in enumerate(frames):
    x = 20 + (i % cols) * (pw + 20)
    y = 20 + (i // cols) * (ph + 40)
    d.text((x, y), name, fill=(30, 30, 40))
    sheet.paste(preview_png(f, scale), (x, y + 16))
sheet.save(sys.argv[1] if len(sys.argv) > 1 else "preview.png")
print("ok")
