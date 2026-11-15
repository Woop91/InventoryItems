"""Measure the matrix refresh rate for a set of options (run on the Pi with the service stopped).

sudo python3 refresh_test.py PWM_BITS LIMIT_HZ [SLOWDOWN] [MAPPING] [LSB_NS]
Prints the library's own refresh-rate readout for ~6 seconds while showing a clock-like frame.
"""
import sys
import time

from PIL import Image, ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions

o = RGBMatrixOptions()
o.rows, o.cols = 32, 64
o.hardware_mapping = sys.argv[4] if len(sys.argv) > 4 else "adafruit-hat"
o.gpio_slowdown = int(sys.argv[3]) if len(sys.argv) > 3 else 4
o.pwm_bits = int(sys.argv[1])
o.limit_refresh_rate_hz = int(sys.argv[2])
o.brightness = 20
if len(sys.argv) > 5:
    o.pwm_lsb_nanoseconds = int(sys.argv[5])
o.show_refresh_rate = True
o.drop_privileges = False
m = RGBMatrix(options=o)
img = Image.new("RGB", (64, 32))
d = ImageDraw.Draw(img)
d.rectangle((4, 4, 59, 20), outline=(235, 235, 235))
d.rectangle((40, 24, 60, 28), fill=(255, 170, 0))
m.SetImage(img)
time.sleep(6)
