#!/usr/bin/env python3
"""Durable Pico LiPo dashboard: USB when attached, LoRa via the Desk otherwise."""
import csv
import argparse
from contextlib import closing
import io
import json
import math
import os
from pathlib import Path
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen

import serial

HERE = Path(__file__).resolve().parent
DEVICE = os.environ.get('LIGHT_DASH_DEVICE',
    '/dev/serial/by-id/usb-MicroPython_Board_in_FS_mode_e4611847673b3e21-if00')
ROOM_API = os.environ.get('LIGHT_DASH_ROOM_API', 'http://127.0.0.1:8771/api/latest')
RANGES = {'10m': 600, '30m': 1800, '2h': 7200, '6h': 21600,
          '24h': 86400, '7d': 604800, '30d': 2592000}
FIELDS = ('scd41_co2', 'scd41_temp_f', 'scd41_hum', 'bme688_temp_f',
          'bme688_hum', 'bme688_hpa', 'bme688_gas_kohm', 'aht10_temp_f',
          'aht10_hum', 'mics6814_red_kohm', 'mics6814_nh3_kohm',
          'mics6814_ox_kohm', 'mics6814_warm_s')
RADIO_FIELDS = {'co2': 'scd41_co2', 'temp_f': 'scd41_temp_f', 'hum': 'scd41_hum',
                'hpa': 'bme688_hpa', 'voc_k': 'bme688_gas_kohm',
                'red_k': 'mics6814_red_kohm', 'nh3_k': 'mics6814_nh3_kohm',
                'ox_k': 'mics6814_ox_kohm', 'bt': 'bme688_temp_f',
                'bh': 'bme688_hum', 'at': 'aht10_temp_f', 'ah': 'aht10_hum'}


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as con, con:
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('CREATE TABLE IF NOT EXISTS samples ('
                        'ts REAL NOT NULL, payload TEXT NOT NULL, source TEXT NOT NULL, '
                        'PRIMARY KEY(ts, source))')

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def add(self, ts, payload, source):
        if not math.isfinite(ts) or not isinstance(payload, dict):
            raise ValueError('invalid sample')
        with closing(self.connect()) as con, con:
            con.execute('INSERT OR IGNORE INTO samples VALUES (?,?,?)',
                        (ts, json.dumps(payload, allow_nan=False), source))

    def read(self, range_name='2h'):
        now = time.time()
        con = self.connect()
        try:
            first, last, total = con.execute('SELECT MIN(ts), MAX(ts), COUNT(*) FROM samples').fetchone()
            start = (first if first is not None else now) if range_name == 'all' else now - RANGES.get(range_name, 7200)
            bucket = max(2, math.ceil((now - start) / 1800))
            cols = ','.join(f"AVG(json_extract(payload, '$.{key}'))" for key in FIELDS)
            rows = con.execute(f'SELECT AVG(ts), {cols} FROM samples WHERE ts >= ? '
                               'GROUP BY CAST(ts / ? AS INTEGER) ORDER BY 1',
                               (start, bucket)).fetchall()
            count = con.execute('SELECT COUNT(*) FROM samples WHERE ts >= ?', (start,)).fetchone()[0]
            latest = con.execute('SELECT ts, payload, source FROM samples ORDER BY ts DESC LIMIT 1').fetchone()
            gap = con.execute('SELECT MAX(ts-prev) FROM (SELECT ts, LAG(ts) OVER (ORDER BY ts) prev '
                              'FROM samples WHERE ts >= ?)', (start,)).fetchone()[0]
            return {'rows': [[r[0], {k: r[i + 1] for i, k in enumerate(FIELDS) if r[i + 1] is not None}] for r in rows],
                    'latest': [latest[0], json.loads(latest[1])] if latest else None,
                    'source': latest[2] if latest else None, 'first': first, 'last': last,
                    'total': total, 'count': count, 'start': start, 'end': now,
                    'bucket': bucket, 'largest_gap_s': gap or 0}
        finally:
            con.close()

    def export(self):
        con = self.connect()
        try:
            yield from con.execute('SELECT ts, payload, source FROM samples ORDER BY ts')
        finally:
            con.close()


def radio_sample(body, now=None):
    now = time.time() if now is None else now
    candidates = []
    for box in body.get('boxes', []):
        age = box.get('age_s')
        if age is None or not isinstance(age, (int, float)) or not 0 <= age <= 30:
            continue
        peer = (box.get('reading') or {}).get('lora', {}).get('peers', {}).get('lipo')
        if not peer or not isinstance(peer.get('age_s'), (int, float)):
            continue
        total_age = age + peer['age_s']
        if not 0 <= total_age <= 45:
            continue
        payload = {dst: peer['d'][src] for src, dst in RADIO_FIELDS.items()
                   if isinstance(peer.get('d', {}).get(src), (int, float))}
        if payload:
            candidates.append((now - total_age, payload, box.get('name', 'Desk'), peer))
    return max(candidates, key=lambda r: r[0]) if candidates else None


class Collector:
    def __init__(self, store):
        self.store = store
        self.lock = threading.Lock()
        self.usb = None
        self.usb_at = 0
        self.usb_error = None
        self.radio_error = 'Waiting for Desk radio relay'
        self.radio = None
        with closing(store.connect()) as con:
            self.last_radio = con.execute("SELECT COALESCE(MAX(ts),0) FROM samples WHERE source='radio'").fetchone()[0]
        self.lora = {'up': None, 'peers': {}, 'messages': [], 'beacons_out': 0, 'last_out': None}

    def serial_reader(self):
        while True:
            try:
                with serial.Serial(DEVICE, 115200, timeout=3) as port:
                    with self.lock:
                        self.usb, self.usb_error = port, None
                    while True:
                        line = port.readline()
                        if line.startswith(b'DATA '):
                            try:
                                payload = json.loads(line[5:])
                                ts = time.time()
                                self.store.add(ts, payload, 'usb')
                                with self.lock:
                                    self.usb_at = ts
                            except (ValueError, TypeError):
                                continue
                        elif line.startswith(b'LORA '):
                            try:
                                self.on_lora(json.loads(line[5:]))
                            except (ValueError, KeyError, TypeError):
                                continue
            except (OSError, serial.SerialException, sqlite3.Error) as exc:
                with self.lock:
                    self.usb, self.usb_error = None, str(exc)
                time.sleep(3)

    def on_lora(self, ev):
        now = time.time()
        with self.lock:
            if ev.get('e') == 'down':
                self.lora.update(up=False, error=ev.get('error'))
                return
            self.lora['up'] = True
            kind = ev.get('e')
            if kind == 'beacon_out':
                self.lora['beacons_out'] += 1
                self.lora['last_out'] = now
            elif kind in ('beacon', 'msg'):
                peer = self.lora['peers'].setdefault(ev['from'], {})
                peer.update(last=now, rssi=ev.get('rssi'), snr=ev.get('snr'))
                if kind == 'beacon':
                    peer['d'] = ev.get('d', {})
                else:
                    self.lora['messages'].append({'t': now, 'in': True, 'who': ev['from'], 'x': ev['x']})
            elif kind == 'sent':
                self.lora['messages'].append({'t': now, 'in': False, 'n': ev['n'], 'x': ev['x'], 'status': 'sending'})
            elif kind in ('ack', 'lost'):
                for msg in self.lora['messages']:
                    if not msg['in'] and msg.get('n') == ev['n']:
                        msg.update(status='delivered' if kind == 'ack' else 'not delivered', who=ev.get('from'))
            self.lora['messages'] = self.lora['messages'][-50:]

    def relay_reader(self):
        while True:
            try:
                with urlopen(ROOM_API, timeout=4) as response:
                    sample = radio_sample(json.load(response))
                with self.lock:
                    self.radio = sample
                    self.radio_error = None if sample else 'No fresh Pico LiPo beacon received by Desk'
                    usb_fresh = time.time() - self.usb_at < 8
                if sample and sample[0] > self.last_radio + 3:
                    if not usb_fresh:
                        self.store.add(sample[0], sample[1], 'radio')
                    self.last_radio = sample[0]
            except (OSError, ValueError, sqlite3.Error) as exc:
                with self.lock:
                    self.radio_error = str(exc)
            time.sleep(5)

    def public(self, range_name):
        result = self.store.read(range_name)
        age = time.time() - result['last'] if result['last'] is not None else None
        with self.lock:
            result.update(serial=self.usb is not None, usb_error=self.usb_error,
                          radio_error=self.radio_error,
                          live=age is not None and 0 <= age < (8 if result['source'] == 'usb' else 45),
                          age_s=age, lora=json.loads(json.dumps(self.lora)),
                          relay=self.radio[2] if self.radio else None,
                          can_send=(self.usb is not None and time.time() - self.usb_at < 8)
                          or (self.radio is not None and self.radio_error is None))
        return result

    def send(self, text):
        with self.lock:
            port = self.usb
            relay = self.radio
        if port is not None:
            port.write(('SEND ' + text + '\n').encode())
            return True
        # The relay has an HTTP send endpoint; target only the configured Desk's IP.
        if relay:
            with urlopen(ROOM_API, timeout=4) as response:
                boxes = json.load(response).get('boxes', [])
            from urllib.parse import urlencode
            for box in boxes:
                if box.get('name', 'Desk') == relay[2] and box.get('age_s', 999) < 30:
                    host = box.get('host')
                    with urlopen(f'http://{host}/send?' + urlencode({'text': text}), timeout=4) as response:
                        return bool(json.load(response).get('queued'))
        return False


def make_handler(collector):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, body, ctype='application/json', code=200):
            if not isinstance(body, bytes):
                body = json.dumps(body).encode()
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            url = urlsplit(self.path)
            if url.path in ('/', '/index.html'):
                return self.send((HERE / 'light_dash.html').read_bytes(), 'text/html; charset=utf-8')
            if url.path == '/data.json':
                range_name = parse_qs(url.query).get('range', ['2h'])[0]
                return self.send(collector.public(range_name))
            if url.path == '/export.csv':
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(['timestamp_unix', 'source', *FIELDS])
                for ts, payload, source in collector.store.export():
                    data = json.loads(payload)
                    writer.writerow([ts, source, *(data.get(k) for k in FIELDS)])
                return self.send(buf.getvalue().encode(), 'text/csv; charset=utf-8')
            self.send({'error': 'not found'}, code=404)

        def do_POST(self):
            if self.path != '/send':
                return self.send({'error': 'not found'}, code=404)
            try:
                n = int(self.headers.get('Content-Length', '0'))
                if not 0 < n <= 2000:
                    raise ValueError('invalid request size')
                text = json.loads(self.rfile.read(n)).get('text', '')
                text = ''.join(c for c in str(text) if c >= ' ' and c != '\x7f').strip()[:180]
                ok = bool(text) and collector.send(text)
                self.send({'queued': ok})
            except (OSError, ValueError, TypeError):
                self.send({'queued': False}, code=400)
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-json', type=Path, help='Import a saved dashboard /data.json response and exit')
    args = parser.parse_args()
    store = Store(os.environ.get('LIGHT_DASH_DB', str(Path.home() / '.local/share/pico-sensors/air-readings.sqlite')))
    if args.import_json:
        saved = json.loads(args.import_json.read_text())
        for ts, payload in saved['rows']:
            store.add(ts, payload, 'usb')
        print(f"Imported {len(saved['rows'])} readings (duplicates ignored)")
        return
    collector = Collector(store)
    threading.Thread(target=collector.serial_reader, daemon=True).start()
    threading.Thread(target=collector.relay_reader, daemon=True).start()
    ThreadingHTTPServer(('127.0.0.1', int(os.environ.get('LIGHT_DASH_PORT', '8772'))), make_handler(collector)).serve_forever()


if __name__ == '__main__':
    main()
