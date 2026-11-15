"""I2C sensors on the Qwiic pHAT: SCD41 (CO2, 0x62) and AHT20 (temperature/humidity, 0x38).

python3 -m pixelclock.sensors     prints one reading from each sensor found.
"""

import time

try:
    from smbus2 import SMBus, i2c_msg
except ImportError:  # preview machines without smbus2
    SMBus = None

SCD41 = 0x62
AHT20 = 0x38


def _crc8(data):
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


class Scd41:
    def __init__(self, bus):
        self.bus = bus
        self.cmd(0x3F86)  # stop periodic measurement, in case it was running
        time.sleep(0.5)
        self.serial = self.read_words(0x3682, 3)
        self.cmd(0x21B1)  # start periodic measurement (a reading every 5 s)

    def cmd(self, c):
        self.bus.i2c_rdwr(i2c_msg.write(SCD41, [c >> 8, c & 0xFF]))

    def read_words(self, c, n, delay=0.002):
        self.cmd(c)
        time.sleep(delay)
        r = i2c_msg.read(SCD41, n * 3)
        self.bus.i2c_rdwr(r)
        raw = list(r)
        words = []
        for i in range(n):
            chunk = raw[i * 3:i * 3 + 2]
            if _crc8(chunk) != raw[i * 3 + 2]:
                raise IOError("SCD41 CRC mismatch")
            words.append(chunk[0] << 8 | chunk[1])
        return words

    def ready(self):
        return (self.read_words(0xE4B8, 1)[0] & 0x07FF) != 0

    def read(self):
        """(co2 ppm, temperature C, humidity %) or None when no new reading is ready."""
        if not self.ready():
            return None
        co2, t, h = self.read_words(0xEC05, 3)
        return co2, -45 + 175 * t / 65535, 100 * h / 65535


class Aht20:
    def __init__(self, bus):
        self.bus = bus
        self.model = "AHT"
        status = self.status()
        if not status & 0x08:  # not calibrated: initialise
            bus.i2c_rdwr(i2c_msg.write(AHT20, [0xBE, 0x08, 0x00]))
            time.sleep(0.01)

    def status(self):
        r = i2c_msg.read(AHT20, 1)
        self.bus.i2c_rdwr(r)
        return list(r)[0]

    def read(self):
        """(temperature C, humidity %)"""
        self.bus.i2c_rdwr(i2c_msg.write(AHT20, [0xAC, 0x33, 0x00]))
        time.sleep(0.09)
        r = i2c_msg.read(AHT20, 7)
        self.bus.i2c_rdwr(r)
        d = list(r)
        if d[0] & 0x80:
            raise IOError("AHT busy")
        # An AHT20 appends a CRC byte; the older AHT10 does not, so only trust a match
        self.model = "AHT20" if _crc8(d[:6]) == d[6] else "AHT10"
        hum = ((d[1] << 12) | (d[2] << 4) | (d[3] >> 4)) * 100 / (1 << 20)
        temp = (((d[3] & 0x0F) << 16) | (d[4] << 8) | d[5]) * 200 / (1 << 20) - 50
        return temp, hum


def open_sensors(busno=1):
    """Return (bus, scd41 or None, aht20 or None)."""
    if SMBus is None:
        return None, None, None
    bus = SMBus(busno)
    scd = aht = None
    try:
        scd = Scd41(bus)
    except OSError:
        pass
    try:
        aht = Aht20(bus)
    except OSError:
        pass
    return bus, scd, aht


def c_to_f(c):
    return c * 9 / 5 + 32


if __name__ == "__main__":
    bus, scd, aht = open_sensors()
    if aht:
        t, h = aht.read()
        print(f"{aht.model}: {c_to_f(t):.1f} F, {h:.0f}% humidity")
    else:
        print("AHT20: not found")
    if scd:
        print("SCD41 serial", "-".join(f"{w:04x}" for w in scd.serial), "- waiting for first reading...")
        for _ in range(15):
            time.sleep(1)
            r = scd.read()
            if r:
                print(f"SCD41: {r[0]} ppm CO2, {c_to_f(r[1]):.1f} F, {r[2]:.0f}% humidity")
                break
    else:
        print("SCD41: not found")
