#!/usr/bin/env python3
"""Desk side of the Pico W sensor boxes: poll each box, keep the history, serve the dashboard.

Every few seconds each box's http://<box>/data.json is read and stored in SQLite; the
dashboard is served on 127.0.0.1 (publish it to the tailnet with `tailscale serve`).

Boxes are known by their Wi-Fi MAC address, so a new DHCP address doesn't matter: when a
box stops answering, or every 10 minutes, the local network is scanned for boxes, moved
ones are found again and new ones are added.

Config: ~/.config/pico-sensors/desk.json, all keys optional:
  {"port": 8771, "poll_s": 5, "subnets": ["192.168.50"],
   "boxes": [{"mac": "28:cd:c1:08:ef:1a", "name": "Desk", "host": "192.168.50.62"}]}
Rename a box by editing its "name" and restarting the service.
Data:   ~/.local/share/pico-sensors/readings.sqlite
"""
import concurrent.futures
import csv
import io
import json
import sqlite3
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CFG_DIR = Path.home() / ".config" / "pico-sensors"
CFG_FILE = CFG_DIR / "desk.json"
DATA_DIR = Path.home() / ".local" / "share" / "pico-sensors"
DB_FILE = DATA_DIR / "readings.sqlite"
DASHBOARD = Path(__file__).resolve().parent / "dashboard.html"

FIELDS = ("co2_ppm", "temp_f", "humidity_pct", "distance_mm", "bpm")
RANGES = {"1h": 3600, "6h": 6 * 3600, "24h": 86400, "7d": 7 * 86400, "30d": 30 * 86400, "all": None}
POINTS = 360          # buckets per chart
RESCAN_S = 600        # look for new boxes this often
RETRY_SCAN_S = 120    # and at most this often while a box is missing

lock = threading.Lock()


def load_cfg():
    try:
        cfg = json.loads(CFG_FILE.read_text())
    except (OSError, ValueError):
        cfg = {}
    if "boxes" not in cfg:                      # first version kept one address under "pico"
        cfg["boxes"] = [{"mac": None, "name": "Desk", "host": cfg.pop("pico")}] if cfg.get("pico") else []
    return cfg


def save_cfg(cfg):
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CFG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2) + "\n")
    tmp.replace(CFG_FILE)


def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_FILE, timeout=10)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""CREATE TABLE IF NOT EXISTS readings (
        ts INTEGER NOT NULL, co2_ppm REAL, temp_f REAL, humidity_pct REAL,
        distance_mm REAL, bpm REAL, finger INTEGER, rssi INTEGER, mac TEXT)""")
    cols = [r[1] for r in con.execute("PRAGMA table_info(readings)")]
    if "mac" not in cols:                       # history from the one-box version
        con.execute("ALTER TABLE readings ADD COLUMN mac TEXT")
    con.execute("CREATE INDEX IF NOT EXISTS readings_mac_ts ON readings(mac, ts)")
    con.execute("CREATE TABLE IF NOT EXISTS latest_snapshots (mac TEXT PRIMARY KEY, ts REAL, payload TEXT)")
    con.commit()
    return con


def arp_mac(host):
    try:
        for line in Path("/proc/net/arp").read_text().splitlines()[1:]:
            parts = line.split()
            if parts[0] == host and parts[3] != "00:00:00:00:00:00":
                return parts[3].lower()
    except OSError:
        pass
    return None


def fetch(host, timeout=3.0):
    with urllib.request.urlopen(f"http://{host}/data.json", timeout=timeout) as r:
        d = json.loads(r.read())
    if d.get("device") != "pico-sensors":
        raise ValueError("not a sensor box")
    return d


class Box:
    def __init__(self, entry):
        self.entry = entry                      # the dict inside cfg["boxes"]
        self.latest = None
        self.latest_at = 0
        self.error = "not polled yet"

    @property
    def mac(self):
        return self.entry.get("mac")

    def public(self):
        return {
            "id": self.mac, "name": self.entry.get("name") or "Sensor box", "host": self.entry.get("host"),
            "reading": self.latest,
            "age_s": None if not self.latest_at else round(time.time() - self.latest_at, 1),
            "error": self.error,
        }


class Service:
    def __init__(self, cfg):
        self.cfg = cfg
        self.boxes = [Box(e) for e in cfg["boxes"]]
        self.last_scan = 0
        self.scanning = False
        con = db()
        try:
            for box in self.boxes:
                row = con.execute("SELECT ts,payload FROM latest_snapshots WHERE mac = ?", (box.mac,)).fetchone()
                if row:
                    box.latest_at, payload = row
                    box.latest = json.loads(payload)
                    box.error = "Waiting for a fresh reading"
                else:
                    old = con.execute("SELECT ts,co2_ppm,temp_f,humidity_pct,distance_mm,bpm "
                                      "FROM readings WHERE mac IS ? ORDER BY ts DESC LIMIT 1", (box.mac,)).fetchone()
                    if old:
                        box.latest_at = old[0]
                        box.latest = dict(zip(FIELDS, old[1:]))
                        box.error = "Waiting for a fresh reading"
        finally:
            con.close()

    # ---------------------------------------------------------------- discovery
    def subnets(self):
        if self.cfg.get("subnets"):
            return self.cfg["subnets"]
        out = subprocess.run(["ip", "-4", "-o", "addr", "show"], capture_output=True, text=True).stdout
        nets = []
        for line in out.splitlines():           # private /24s on real interfaces, not Docker or VMs
            parts = line.split()
            dev, addr = parts[1], parts[3].split("/")[0]
            if dev.startswith(("eno", "enp", "eth", "wl")) and addr.startswith(("192.168.", "10.", "172.")):
                nets.append(addr.rsplit(".", 1)[0])
        return nets

    def scan(self):
        self.last_scan = time.time()
        hosts = [f"{net}.{i}" for net in self.subnets() for i in range(1, 255)]
        found = []
        with concurrent.futures.ThreadPoolExecutor(64) as ex:
            futs = {ex.submit(fetch, h, 0.8): h for h in hosts}
            for f in concurrent.futures.as_completed(futs):
                if f.exception() is None:
                    host, d = futs[f], f.result()
                    found.append((host, (d.get("mac") or arp_mac(host) or "").lower() or None, d))
        changed = False
        with lock:
            for host, mac, d in found:
                box = next((b for b in self.boxes if mac and b.mac == mac), None)
                if box is None:
                    box = next((b for b in self.boxes if not b.mac and b.entry.get("host") == host), None)
                if box is None:
                    entry = {"mac": mac, "name": d.get("name") or f"Box {len(self.boxes) + 1}", "host": host}
                    self.cfg["boxes"].append(entry)
                    box = Box(entry)
                    self.boxes.append(box)
                    threading.Thread(target=self.poll, args=(box,), daemon=True).start()
                    changed = True
                if box.entry.get("host") != host or (mac and box.mac != mac):
                    box.entry["host"] = host
                    if mac:
                        box.entry["mac"] = mac
                    changed = True
            if changed:
                save_cfg(self.cfg)

    def scan_soon(self, urgent):
        due = RETRY_SCAN_S if urgent else RESCAN_S
        with lock:
            if self.scanning or time.time() - self.last_scan < due:
                return
            self.scanning = True
        try:
            self.scan()
        finally:
            self.scanning = False

    # ---------------------------------------------------------------- polling
    def poll(self, box):
        con = db()
        while True:
            host = box.entry.get("host")
            try:
                if not host:
                    raise OSError("address unknown")
                d = fetch(host)
                mac = (d.get("mac") or arp_mac(host) or "").lower() or None
                if mac and box.mac != mac:
                    with lock:
                        box.entry["mac"] = mac
                        save_cfg(self.cfg)
                    # rows saved before this box's MAC was known belong to it
                    con.execute("UPDATE readings SET mac = ? WHERE mac IS NULL", (mac,))
                stamp = time.time()
                con.execute("INSERT INTO readings VALUES (?,?,?,?,?,?,?,?,?)", (
                    int(stamp), d.get("co2_ppm"), d.get("temp_f"), d.get("humidity_pct"),
                    d.get("distance_mm"), d.get("bpm"), int(bool(d.get("finger"))), d.get("rssi"), box.mac))
                con.execute("INSERT OR REPLACE INTO latest_snapshots VALUES (?,?,?)",
                            (box.mac, stamp, json.dumps(d)))
                con.commit()
                with lock:
                    box.latest, box.latest_at, box.error = d, stamp, None
            except Exception as e:  # noqa: BLE001 - any failure means "box offline"
                con.rollback()
                box.error = f"{type(e).__name__}: {e}"
                threading.Thread(target=self.scan_soon, args=(True,), daemon=True).start()
            time.sleep(self.cfg.get("poll_s", 5))

    def background_scans(self):
        while True:
            self.scan_soon(False)
            time.sleep(60)

    def start(self):
        for b in self.boxes:
            threading.Thread(target=self.poll, args=(b,), daemon=True).start()
        threading.Thread(target=self.background_scans, daemon=True).start()

    def box(self, box_id):
        if not box_id:
            return self.boxes[0] if self.boxes else None
        return next((b for b in self.boxes if b.mac == box_id), None)


def history(con, mac, span):
    now = int(time.time())
    if span is None:
        first = con.execute("SELECT MIN(ts) FROM readings WHERE mac IS ?", (mac,)).fetchone()[0]
        span = max(60, now - first + 1) if first is not None else 86400
    start = now - span
    bucket = max(5, span // POINTS)
    cols = ", ".join(f"AVG({f})" for f in FIELDS)
    rows = con.execute(
        f"SELECT (ts / ?) * ? AS b, {cols} FROM readings WHERE mac IS ? AND ts >= ? GROUP BY b ORDER BY b",
        (bucket, bucket, mac, start)).fetchall()
    stats = {}
    for f in FIELDS:
        mn, mx, av = con.execute(
            f"SELECT MIN({f}), MAX({f}), AVG({f}) FROM readings WHERE mac IS ? AND ts >= ? AND {f} IS NOT NULL",
            (mac, start)).fetchone()
        stats[f] = {"min": mn, "max": mx, "avg": av}
    first, last, count = con.execute(
        "SELECT MIN(ts), MAX(ts), COUNT(*) FROM readings WHERE mac IS ?", (mac,)).fetchone()
    largest_gap = con.execute(
        "SELECT MAX(ts-prev) FROM (SELECT ts,LAG(ts) OVER (ORDER BY ts) prev "
        "FROM readings WHERE mac IS ? AND ts >= ?)", (mac, start)).fetchone()[0]
    return {
        "start": start, "end": now, "bucket": bucket,
        "t": [r[0] for r in rows],
        **{f: [None if r[i + 1] is None else round(r[i + 1], 1) for r in rows] for i, f in enumerate(FIELDS)},
        "stats": stats,
        "box": mac,
        "coverage": {"first": first, "last": last, "count": count,
                     "largest_gap_s": largest_gap or 0},
    }


def make_handler(svc):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype="application/json", extra=None):
            if isinstance(body, (dict, list)):
                body = json.dumps(body)
            if isinstance(body, str):
                body = body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(u.query)
            arg = lambda k, d=None: q.get(k, [d])[0]  # noqa: E731
            if u.path in ("/", "/index.html"):
                return self.send(200, DASHBOARD.read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/latest":
                return self.send(200, {"boxes": [b.public() for b in svc.boxes]})
            if u.path == "/api/history":
                b = svc.box(arg("box"))
                if b is None:
                    return self.send(404, {"error": "no boxes yet"})
                con = db()
                try:
                    return self.send(200, history(con, b.mac, RANGES.get(arg("range", "24h"), 86400)))
                finally:
                    con.close()
            if u.path == "/export.csv":
                span = RANGES.get(arg("range", "30d"), 30 * 86400)
                names = {b.mac: b.entry.get("name") for b in svc.boxes}
                con = db()
                try:
                    rows = con.execute(
                        "SELECT ts, mac, co2_ppm, temp_f, humidity_pct, distance_mm, bpm FROM readings "
                        "WHERE ts >= ? ORDER BY ts", (int(time.time()) - span if span is not None else 0,)).fetchall()
                finally:
                    con.close()
                buf = io.StringIO()
                w = csv.writer(buf)
                w.writerow(["time_et", "box", "co2_ppm", "temp_f", "humidity_pct", "distance_mm", "bpm"])
                for r in rows:
                    w.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r[0])),
                                names.get(r[1], r[1]), *r[2:]])
                return self.send(200, buf.getvalue(), "text/csv",
                                 {"Content-Disposition": "attachment; filename=pico-sensors.csv"})
            self.send(404, {"error": "not found"})

    return H


def main():
    cfg = load_cfg()
    save_cfg(cfg)
    db().close()
    svc = Service(cfg)
    svc.start()
    ThreadingHTTPServer(("127.0.0.1", cfg.get("port", 8771)), make_handler(svc)).serve_forever()


if __name__ == "__main__":
    main()
