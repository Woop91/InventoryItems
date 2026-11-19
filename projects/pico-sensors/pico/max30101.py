"""MAX30101 pulse sensor: raw red/IR samples, finger detection and a heart-rate estimate.

The estimate finds IR pulse peaks after removing the slow (DC) part of the signal.
It is a hobby reading, not a medical one, and there is no SpO2 figure on purpose.
"""
import time

ADDR = 0x57
FINGER_IR = 30000          # IR level above this means a finger is resting on the sensor


class MAX30101:
    def __init__(self, i2c, address=ADDR):
        self.i2c = i2c
        self.address = address
        if self._r(0xFF) != 0x15:
            raise OSError("MAX30101 not found at 0x%02x" % address)
        self._w(0x09, 0x40)                      # reset
        time.sleep_ms(10)
        self._w(0x08, 0x5F)                      # FIFO: average 4 samples, roll over, almost-full at 17
        self._w(0x0A, 0x27)                      # SpO2 config: 4096 nA range, 100 samples/s, 411 us pulses (18 bit)
        self._w(0x0C, 0x24)                      # red LED about 7 mA
        self._w(0x0D, 0x24)                      # IR LED about 7 mA
        self._w(0x09, 0x03)                      # SpO2 mode: red + IR
        self._clear_fifo()
        self.sample_hz = 25                      # 100 samples/s averaged by 4
        self._dc = None
        self._prev = 0
        self._rising = False
        self._last_peak = None
        self._n = 0
        self._intervals = []
        self.ir = 0
        self.red = 0

    def _w(self, reg, v):
        self.i2c.writeto_mem(self.address, reg, bytes([v]))

    def _r(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def _clear_fifo(self):
        for reg in (0x04, 0x05, 0x06):
            self._w(reg, 0)

    def finger(self):
        return self.ir > FINGER_IR

    def update(self):
        """Read every waiting sample. Call at least a few times a second."""
        n = (self._r(0x04) - self._r(0x06)) & 0x1F
        if n == 0:
            return
        data = self.i2c.readfrom_mem(self.address, 0x07, 6 * n)
        for i in range(n):
            b = data[6 * i:6 * i + 6]
            self.red = ((b[0] << 16) | (b[1] << 8) | b[2]) & 0x3FFFF
            self.ir = ((b[3] << 16) | (b[4] << 8) | b[5]) & 0x3FFFF
            self._beat(self.ir)

    def _beat(self, ir):
        self._n += 1
        if ir < FINGER_IR:
            self._dc = None
            self._intervals = []
            self._last_peak = None
            return
        self._dc = ir if self._dc is None else self._dc + (ir - self._dc) / 16
        ac = ir - self._dc
        if ac > self._prev:
            self._rising = True
        elif self._rising and ac < self._prev and self._prev > 20:
            # just passed a peak
            self._rising = False
            if self._last_peak is not None:
                gap = self._n - self._last_peak
                if self.sample_hz * 60 // 200 <= gap <= self.sample_hz * 60 // 40:   # 40-200 bpm
                    self._intervals = (self._intervals + [gap])[-8:]
            self._last_peak = self._n
        self._prev = ac

    def bpm(self):
        """Heart rate estimate once a finger has rested long enough, else None."""
        if not self.finger() or len(self._intervals) < 4:
            return None
        s = sorted(self._intervals)
        mid = s[len(s) // 2]
        return round(self.sample_hz * 60 / mid)

    def temperature(self):
        """Die temperature in C (reads warm; useful as a sanity check only)."""
        self._w(0x21, 0x01)
        time.sleep_ms(30)
        return self._r(0x1F) - (256 if self._r(0x1F) > 127 else 0) + self._r(0x20) * 0.0625
