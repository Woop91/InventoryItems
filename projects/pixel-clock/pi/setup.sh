#!/bin/bash
# Installs the pixel clock on Raspberry Pi OS Lite (Trixie). Safe to run again.
# First boot runs it from /boot/firmware/pixelclock/; later runs: sudo bash /opt/pixelclock/pi/setup.sh
set -euo pipefail
exec > >(tee -a /var/log/pixelclock-setup.log) 2>&1
echo "=== pixelclock setup $(date)"

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST=/opt/pixelclock

# Wait for the network (first boot)
for i in $(seq 1 60); do getent hosts deb.debian.org >/dev/null && break; sleep 5; done
# ...and for the clock: a Pi has no battery clock, and apt rejects signatures "not live yet"
for i in $(seq 1 60); do
  [ "$(timedatectl show -p NTPSynchronized --value)" = yes ] && break; sleep 5
done

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends git build-essential python3-dev python3-pil \
    python3-setuptools python3-pip cython3 cmake ninja-build avahi-daemon iw \
    i2c-tools python3-smbus2

# I2C for the sensors on the Qwiic pHAT (SCD41, AHT10/AHT20)
sed -i 's/^#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/firmware/config.txt
echo i2c-dev > /etc/modules-load.d/i2c.conf
modprobe i2c-dev || true
dtparam i2c_arm=on 2>/dev/null || true

# rgbmatrix library (hzeller), Python bindings
if ! python3 -c "import rgbmatrix" 2>/dev/null; then
  rm -rf /opt/rpi-rgb-led-matrix
  git clone --depth 1 https://github.com/hzeller/rpi-rgb-led-matrix /opt/rpi-rgb-led-matrix
  cd /opt/rpi-rgb-led-matrix
  if grep -q "build-python" Makefile; then
    make build-python PYTHON="$(command -v python3)"
    make install-python PYTHON="$(command -v python3)"
  else
    python3 -m pip install --break-system-packages .
  fi
  cd /
fi
python3 -c "import rgbmatrix; print('rgbmatrix ok')"

# App files
if [ "$SRC" != "$DEST" ]; then
  mkdir -p "$DEST"
  cp -r "$SRC"/pixelclock "$SRC"/pi "$DEST"/
fi
if [ ! -f /etc/pixelclock.json ] && [ -f "$SRC/pixelclock.json" ]; then
  install -m 600 "$SRC/pixelclock.json" /etc/pixelclock.json
fi

# Snappy: no onboard audio (it fights the matrix timing), no Wi-Fi power saving, fewer services
grep -q "^blacklist snd_bcm2835" /etc/modprobe.d/pixelclock.conf 2>/dev/null || \
  echo "blacklist snd_bcm2835" > /etc/modprobe.d/pixelclock.conf
mkdir -p /etc/NetworkManager/conf.d
printf '[connection]\nwifi.powersave = 2\n' > /etc/NetworkManager/conf.d/pixelclock-powersave.conf
for s in bluetooth hciuart ModemManager triggerhappy cups; do
  systemctl disable --now "$s" 2>/dev/null || true
done

install -m 644 "$DEST/pi/pixelclock.service" /etc/systemd/system/pixelclock.service
systemctl daemon-reload
systemctl enable pixelclock.service
systemctl restart pixelclock.service || true
systemctl reload NetworkManager 2>/dev/null || true
touch /var/lib/pixelclock-setup-done
echo "=== done $(date)"
