"""VL53L1X time-of-flight distance sensor, short and simple.

Register setup is ST's ultra-lite driver default configuration (registers 0x2D-0x87),
as published in the MIT-licensed MicroPython port at github.com/drakxtwo/vl53l1x_pico.
"""
import time

_DEFAULT_CONFIG = bytes([
    0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x02, 0x08, 0x00, 0x08, 0x10, 0x01,
    0x01, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x20, 0x0b, 0x00, 0x00, 0x02, 0x0a, 0x21, 0x00, 0x00, 0x05, 0x00,
    0x00, 0x00, 0x00, 0xc8, 0x00, 0x00, 0x38, 0xff, 0x01, 0x00, 0x08, 0x00,
    0x00, 0x01, 0xdb, 0x0f, 0x01, 0xf1, 0x0d, 0x01, 0x68, 0x00, 0x80, 0x08,
    0xb8, 0x00, 0x00, 0x00, 0x00, 0x0f, 0x89, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x01, 0x0f, 0x0d, 0x0e, 0x0e, 0x00, 0x00, 0x02, 0xc7, 0xff,
    0x9B, 0x00, 0x00, 0x00, 0x01, 0x01, 0x40,
])

# RESULT__RANGE_STATUS values that mean the distance can be trusted.
_GOOD = (9,)


class VL53L1X:
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self.address = address
        self._w8(0x0000, 0x00)          # soft reset
        time.sleep_ms(2)
        self._w8(0x0000, 0x01)
        time.sleep_ms(5)
        if self._r16(0x010F) != 0xEACC:
            raise OSError("VL53L1X not found at 0x%02x" % address)
        self.i2c.writeto_mem(address, 0x2D, _DEFAULT_CONFIG, addrsize=16)   # also starts ranging
        self._w16(0x001E, self._r16(0x0022) * 4)
        time.sleep_ms(200)

    def _w8(self, reg, v):
        self.i2c.writeto_mem(self.address, reg, bytes([v]), addrsize=16)

    def _w16(self, reg, v):
        self.i2c.writeto_mem(self.address, reg, bytes([(v >> 8) & 0xFF, v & 0xFF]), addrsize=16)

    def _r16(self, reg):
        d = self.i2c.readfrom_mem(self.address, reg, 2, addrsize=16)
        return (d[0] << 8) | d[1]

    def ready(self):
        # GPIO__TIO_HV_STATUS bit 0 equals the inverse of the polarity bit when a sample is ready
        pol = (self.i2c.readfrom_mem(self.address, 0x0030, 1, addrsize=16)[0] >> 4) & 1
        return (self.i2c.readfrom_mem(self.address, 0x0031, 1, addrsize=16)[0] & 1) == (0 if pol else 1)

    def read(self):
        """Distance in mm, or None when nothing is in range."""
        d = self.i2c.readfrom_mem(self.address, 0x0089, 17, addrsize=16)
        self._w8(0x0086, 0x01)          # clear interrupt, next sample
        status, mm = d[0] & 0x1F, (d[13] << 8) | d[14]
        return mm if status in _GOOD else None
