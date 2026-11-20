import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def serve(handler):
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class RoomHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.room = module('room', ROOT / 'pico-sensors/desk/pico_sensors_desk.py')
        self.room.DATA_DIR = Path(self.tmp.name)
        self.room.DB_FILE = self.room.DATA_DIR / 'readings.sqlite'
        self.con = self.room.db()
        self.addCleanup(self.con.close)

    def test_unknown_room_does_not_show_desk(self):
        svc = self.room.Service({'boxes': [{'mac': 'desk', 'name': 'Desk'}]})
        self.assertIsNone(svc.box('missing'))

    def test_history_endpoint_rejects_unknown_room(self):
        svc = self.room.Service({'boxes': [{'mac': 'desk', 'name': 'Desk'}]})
        with serve(self.room.make_handler(svc)) as url:
            with self.assertRaises(HTTPError) as raised:
                urlopen(url + '/api/history?box=missing', timeout=3)
            self.assertEqual(raised.exception.code, 404)
            raised.exception.close()

    def test_legacy_latest_restored_without_claiming_it_is_live(self):
        stamp = int(self.room.time.time()) - 600
        self.con.execute('INSERT INTO readings VALUES (?,?,?,?,?,?,?,?,?)',
                         (stamp, 800, 72, 40, None, None, 0, -60, 'desk'))
        self.con.commit()
        box = self.room.Service({'boxes': [{'mac': 'desk'}]}).boxes[0].public()
        self.assertEqual(box['reading']['co2_ppm'], 800)
        self.assertGreaterEqual(box['age_s'], 600)

    def test_saved_latest_restored_with_real_age(self):
        stamp = self.room.time.time() - 600
        self.con.execute('INSERT INTO latest_snapshots VALUES (?,?,?)',
                         ('desk', stamp, json.dumps({'co2_ppm': 810})))
        self.con.commit()
        box = self.room.Service({'boxes': [{'mac': 'desk'}]}).boxes[0].public()
        self.assertEqual(box['reading']['co2_ppm'], 810)
        self.assertGreaterEqual(box['age_s'], 600)

    def test_history_exposes_real_gap_and_keeps_older_rows(self):
        now = int(self.room.time.time())
        for ts in (now - 7200, now - 7100, now - 10):
            self.con.execute('INSERT INTO readings VALUES (?,?,?,?,?,?,?,?,?)',
                             (ts, 800, 72, 40, None, None, 0, -60, 'desk'))
        self.con.commit()
        result = self.room.history(self.con, 'desk', 86400)
        self.assertEqual(result['coverage']['count'], 3)
        self.assertEqual(result['coverage']['largest_gap_s'], 7090)
        self.assertEqual(result['coverage']['first'], now - 7200)


class AirHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.air = module('air', ROOT / 'pico-lipo-light/desk/light_dash.py')
        self.store = self.air.Store(Path(self.tmp.name) / 'air.sqlite')

    def test_history_survives_restart_and_is_not_limited_to_two_hours(self):
        now = self.air.time.time()
        self.store.add(now - 86400, {'scd41_co2': 700}, 'usb')
        self.store.add(now, {'scd41_co2': 900, 'aht10_temp_f': 75}, 'usb')
        reopened = self.air.Store(self.store.path)
        result = reopened.read('7d')
        self.assertEqual(result['count'], 2)
        self.assertEqual(result['latest'][1]['aht10_temp_f'], 75)
        self.assertEqual(len(result['rows']), 2)
        self.assertEqual(reopened.read('10m')['count'], 1)

    def test_radio_reading_uses_sample_age_and_does_not_invent_missing_sensors(self):
        box = {'id': 'desk', 'age_s': 2, 'reading': {'lora': {'peers': {
            'lipo': {'age_s': 8, 'd': {'co2': 880, 'temp_f': 75, 'hum': 43,
                                    'hpa': 1025, 'voc_k': 63, 'nh3_k': 56}}}}}}
        sample = self.air.radio_sample({'boxes': [box]}, now=1000)
        self.assertEqual(sample[0], 990)
        self.assertEqual(sample[1]['scd41_co2'], 880)
        self.assertEqual(sample[1]['bme688_hpa'], 1025)
        self.assertNotIn('aht10_temp_f', sample[1])
        box['age_s'] = 60
        self.assertIsNone(self.air.radio_sample({'boxes': [box]}, now=1000))

    def test_duplicate_sample_is_saved_once(self):
        self.store.add(1000, {'scd41_co2': 800}, 'radio')
        self.store.add(1000, {'scd41_co2': 800}, 'radio')
        self.assertEqual(self.store.read('all')['count'], 1)

    def test_api_shows_old_values_as_offline_and_preserves_all_history(self):
        stamp = self.air.time.time() - 86400
        self.store.add(stamp, {'scd41_co2': 800}, 'usb')
        collector = self.air.Collector(self.air.Store(self.store.path))
        with serve(self.air.make_handler(collector)) as url:
            with urlopen(url + '/data.json?range=all', timeout=3) as response:
                result = json.load(response)
                self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertFalse(result['live'])
            self.assertEqual(result['latest'], [stamp, {'scd41_co2': 800}])
            self.assertEqual(result['count'], 1)
            self.assertEqual(result['rows'][0][1]['scd41_co2'], 800)


if __name__ == '__main__':
    unittest.main()
