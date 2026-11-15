#!/usr/bin/env python3
"""Desktop -> pixel clock bridge. Runs on the workstation as a user service.

Feeds the panel:
  t3        running agent count, threads waiting on you, finished today (T3 state DB, read-only,
            only the small in-progress / pending indexes plus lookups by thread id)
  notify    "needs you", "finished" and "failed" pop-ups for top-level T3 threads,
            plus every desktop notification (org.freedesktop.Notifications)
  system    CPU, GPU and memory load, GPU temperature
  reminder  the next Grokbot reminder

Config: ~/.config/pixelclock/bridge.json  {"host": "pixelclock.local", "port": 8765}
Token:  ~/.config/pixelclock/token
"""

import json
import os
import re
import sqlite3
import subprocess
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
CFG_DIR = Path.home() / ".config/pixelclock"
STATE_DIR = Path.home() / ".local/state/pixelclock"
DB = Path.home() / ".t3/userdata/statev2.sqlite"
IN_PROGRESS = ("queued", "preparing", "starting", "running", "waiting")


def log(*a):
    print(datetime.now(ET).strftime("%I:%M:%S %p ET"), *a, flush=True)


class Panel:
    def __init__(self):
        cfg = {}
        p = CFG_DIR / "bridge.json"
        if p.exists():
            cfg = json.loads(p.read_text())
        self.base = f"http://{cfg.get('host', 'pixelclock.local')}:{cfg.get('port', 8765)}"
        self.token = (CFG_DIR / "token").read_text().strip()
        self.ok = None

    def post(self, path, body):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "X-Token": self.token})
        try:
            with urllib.request.urlopen(req, timeout=4) as r:
                r.read()
            if self.ok is not True:
                log("panel reachable at", self.base)
            self.ok = True
        except Exception as e:
            if self.ok is not False:
                log("panel unreachable:", e)
            self.ok = False

    def notify(self, icon, title, text, color, duration=0):
        key, now = (title, text), time.time()
        recent = getattr(self, "_recent", {})
        if now - recent.get(key, 0) < 15:  # the same pop-up twice in a row
            return
        recent[key] = now
        self._recent = {k: v for k, v in recent.items() if now - v < 60}
        log("notify", title, "|", text)
        self.post("/notify", {"icon": icon, "title": title, "text": text, "color": color,
                              "duration": duration})


# ---------- T3 ----------

class T3Watch:
    def __init__(self, panel):
        self.panel = panel
        self.prev_running = None
        self.prev_pending = None
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.count_file = STATE_DIR / "t3-done.json"
        self.counts = {"day": "", "done": 0, "failed": 0}
        if self.count_file.exists():
            try:
                self.counts = json.loads(self.count_file.read_text())
            except json.JSONDecodeError:
                pass
        self.meta_cache = {}

    def con(self):
        c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=5)
        c.row_factory = sqlite3.Row
        return c

    def meta(self, c, tid):
        """Title and whether this is a top-level thread, by thread id."""
        if tid in self.meta_cache:
            return self.meta_cache[tid]
        r = c.execute("select title, payload_json from orchestration_v2_projection_threads "
                      "where thread_id = ?", (tid,)).fetchone()
        if r is None:
            m = ("", False)
        else:
            p = json.loads(r["payload_json"] or "{}")
            lineage = p.get("lineage") or {}
            top = (not tid.startswith("thread:delegated-task:")
                   and lineage.get("relationshipToParent") != "subagent"
                   and p.get("createdBy") != "agent")
            m = (r["title"], top)
        self.meta_cache[tid] = m
        return m

    def tick(self):
        today = datetime.now(ET).strftime("%Y-%m-%d")
        if self.counts.get("day") != today:
            self.counts = {"day": today, "done": 0, "failed": 0}
        with self.con() as c:
            running = {r[0] for r in c.execute(
                "select distinct thread_id from orchestration_v2_projection_runs "
                "where status in (%s)" % ",".join("?" * len(IN_PROGRESS)), IN_PROGRESS)}
            pending = {r[0] for r in c.execute(
                "select distinct thread_id from orchestration_v2_projection_runtime_requests "
                "where status = 'pending'")}
            top_running = {t for t in running if self.meta(c, t)[1]}
            top_pending = {t for t in pending if self.meta(c, t)[1]}
            if self.prev_pending is not None:
                for tid in top_pending - self.prev_pending:
                    self.panel.notify("bell", "Needs you", self.meta(c, tid)[0], [255, 170, 0], 12)
            if self.prev_running is not None:
                for tid in self.prev_running - top_running:
                    r = c.execute("select status from orchestration_v2_projection_runs where thread_id = ? "
                                  "order by ordinal desc limit 1", (tid,)).fetchone()
                    status = r[0] if r else "completed"
                    title = self.meta(c, tid)[0]
                    if status == "failed":
                        self.counts["failed"] += 1
                        self.panel.notify("cross", "T3 failed", title, [255, 50, 50], 10)
                    elif status in IN_PROGRESS:
                        continue
                    else:
                        self.counts["done"] += 1
                        self.panel.notify("check", "T3 done", title, [40, 220, 80], 8)
                self.count_file.write_text(json.dumps(self.counts))
            self.prev_running, self.prev_pending = top_running, top_pending
            titles = [self.meta(c, t)[0] for t in sorted(top_pending)][:3]
        self.panel.post("/state", {"t3": {
            "running": len(running), "top_running": len(top_running), "waiting": len(top_pending),
            "waiting_titles": titles, "done_today": self.counts["done"], "failed_today": self.counts["failed"],
        }})


# ---------- Desktop notifications ----------

def desktop_notifications(panel):
    """Follow org.freedesktop.Notifications.Notify calls on the session bus."""
    while True:
        try:
            p = subprocess.Popen(
                ["dbus-monitor", "--session", "type='method_call',interface='org.freedesktop.Notifications',"
                 "member='Notify'"], stdout=subprocess.PIPE, text=True)
            strings, inside = [], False
            for line in p.stdout:
                line = line.rstrip("\n")
                if "member=Notify" in line:
                    inside, strings = True, []
                    continue
                if not inside:
                    continue
                m = re.match(r'\s+string "(.*)"$', line)
                if m:
                    strings.append(m.group(1))
                elif line.strip().startswith("array [") and len(strings) >= 4:
                    # app_name, app_icon, summary, body come before the actions array
                    app, _icon, summary, body = strings[:4]
                    inside = False
                    if app.lower() in ("notify-send", "") and summary.startswith("pixelclock"):
                        continue
                    body = re.sub(r"<[^>]+>", "", body)
                    icon = "mail" if "mail" in app.lower() else "chat"
                    panel.notify(icon, app or "Desktop", f"{summary} {body}".strip()[:140], [190, 70, 255])
        except Exception as e:
            log("dbus-monitor error:", e)
        time.sleep(10)


# ---------- System ----------

class Sys:
    def __init__(self):
        self.prev = None

    def cpu(self):
        with open("/proc/stat") as f:
            v = [int(x) for x in f.readline().split()[1:]]
        idle, total = v[3] + v[4], sum(v)
        if self.prev is None:
            self.prev = (idle, total)
            return 0
        di, dt = idle - self.prev[0], total - self.prev[1]
        self.prev = (idle, total)
        return round(100 * (1 - di / dt)) if dt else 0

    def read(self):
        m = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":")
                m[k] = int(v.split()[0])
        mem = round(100 * (1 - m["MemAvailable"] / m["MemTotal"]))
        gpu, gtemp = 0, None
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu",
                                  "--format=csv,noheader,nounits"], capture_output=True, text=True,
                                 timeout=5).stdout
            rows = [[int(x) for x in r.split(",")] for r in out.strip().splitlines() if r.strip()]
            gpu = max(r[0] for r in rows)
            gtemp = max(r[1] for r in rows)
        except Exception:
            pass
        d = {"cpu": self.cpu(), "gpu": gpu, "mem": mem}
        if gtemp is not None:
            d["gpu_temp"] = gtemp
        return d


# ---------- Reminders ----------

REM_RE = re.compile(r"^(\w{8})\s+pending\s+\S+\s+(\w{3} \w{3} \d+, \d{4} \d+:\d+ [AP]M) E[SD]T\s{2,}(.*?)\s{2,}(.*)$")


def next_reminder():
    out = subprocess.run(["grokbot-remind", "list"], capture_output=True, text=True, timeout=20).stdout
    now = datetime.now(ET)
    best = None
    for line in out.splitlines():
        m = REM_RE.match(line)
        if not m:
            continue
        when = datetime.strptime(m.group(2), "%a %b %d, %Y %I:%M %p").replace(tzinfo=ET)
        if when >= now and (best is None or when < best[0]):
            best = (when, m.group(3).strip(), m.group(4).strip())
    if not best:
        return None
    when, owner, text = best
    day = "" if when.date() == now.date() else when.strftime("%a")
    return {"when": when.strftime("%-I:%M"), "ampm": when.strftime("%p"), "day": day,
            "text": text[:80] or owner}


LOG_MIRROR = Path.home() / ".local/share/pixelclock/logs"


def mirror_logs(panel):
    """Copy the Pi's monthly sensor CSVs here, so the readings survive the SD card."""
    LOG_MIRROR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(panel.base + "/log", timeout=10) as r:
        names = json.load(r)
    for name in names:
        if "/" in name or not name.endswith(".csv"):
            continue
        dest = LOG_MIRROR / name
        with urllib.request.urlopen(panel.base + "/log/" + name, timeout=30) as r:
            data = r.read()
        # The Pi's file only grows; never replace a longer local copy with a shorter one
        if not dest.exists() or len(data) >= dest.stat().st_size:
            tmp = dest.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.replace(dest)


def main():
    panel = Panel()
    t3 = T3Watch(panel)
    sysmon = Sys()
    threading.Thread(target=desktop_notifications, args=(panel,), daemon=True).start()
    last_rem = last_mirror = 0
    while True:
        if time.time() - last_mirror > 600:
            last_mirror = time.time()
            try:
                mirror_logs(panel)
            except Exception as e:
                log("log mirror error:", e)
        try:
            t3.tick()
        except Exception as e:
            log("t3 error:", e)
        try:
            panel.post("/state", {"system": sysmon.read()})
        except Exception as e:
            log("system error:", e)
        if time.time() - last_rem > 300:
            last_rem = time.time()
            try:
                r = next_reminder()
                panel.post("/state", {"reminder": r or {}})
            except Exception as e:
                log("reminder error:", e)
        time.sleep(10)


if __name__ == "__main__":
    main()
