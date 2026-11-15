#!/bin/bash
# Customise a mounted Raspberry Pi OS (Trixie, cloud-init) boot partition for the pixel clock.
# Usage: prepare_boot.sh /path/to/bootfs WIFI_CONNECTION_NAME PUBKEY_FILE [PUBKEY_FILE...]
# The Wi-Fi key is read from this machine's NetworkManager profile; it never enters the repo.
set -euo pipefail
B="$1"; CONN="$2"; shift 2
HERE="$(cd "$(dirname "$0")/.." && pwd)"

SSID="$(nmcli -g 802-11-wireless.ssid connection show "$CONN")"
PSK="$(nmcli -s -g 802-11-wireless-security.psk connection show "$CONN")"
KEYS=""
for k in "$@"; do KEYS+="      - $(cat "$k")"$'\n'; done

cat > "$B/user-data" <<EOF
#cloud-config
hostname: pixelclock
manage_etc_hosts: true
timezone: America/New_York
locale: en_US.UTF-8
users:
  - name: pi
    groups: [adm, dialout, gpio, i2c, spi, sudo, video, netdev]
    shell: /bin/bash
    sudo: "ALL=(ALL) NOPASSWD:ALL"
    lock_passwd: true
    ssh_authorized_keys:
${KEYS}
ssh_pwauth: false
enable_ssh: true
runcmd:
  - [systemctl, enable, --now, ssh]
  - [bash, /boot/firmware/pixelclock/pi/setup.sh]
EOF

umask 077
cat > "$B/network-config" <<EOF
network:
  version: 2
  wifis:
    wlan0:
      dhcp4: true
      optional: true
      regulatory-domain: US
      access-points:
        "${SSID}":
          password: "${PSK}"
EOF
umask 022

touch "$B/ssh"
grep -q "isolcpus=3" "$B/cmdline.txt" || sed -i 's/$/ isolcpus=3 irqaffinity=0-2/' "$B/cmdline.txt"
sed -i 's/^dtparam=audio=on/dtparam=audio=off/' "$B/config.txt"

mkdir -p "$B/pixelclock"
cp -r "$HERE/pixelclock" "$HERE/pi" "$B/pixelclock/"
find "$B/pixelclock" -name __pycache__ -prune -exec rm -rf {} +
if [ -n "${PIXELCLOCK_TOKEN:-}" ]; then
  printf '{"token": "%s"}\n' "$PIXELCLOCK_TOKEN" > "$B/pixelclock/pixelclock.json"
fi
sync
echo "boot partition ready: ssid=${SSID} keys=$# token=${PIXELCLOCK_TOKEN:+set}"
