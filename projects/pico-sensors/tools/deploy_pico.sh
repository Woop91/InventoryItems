#!/usr/bin/env bash
# Copy the program to a Pico W over USB and restart it.
#   tools/deploy_pico.sh [--port PORT] [--wifi NM_PROFILE --name "Room 2" --hostname pico-sensors-2]
# --port      the serial port; default: the only MicroPython board on USB
# --wifi      also write config.json, taking the Wi-Fi name and password from this
#             machine's saved NetworkManager profile (must be a 2.4 GHz network)
# --name      the box's name on the dashboard (with --wifi)
# --hostname  its network hostname (with --wifi)
# `mpremote resume` is used throughout: a soft reset would stop the timer that feeds
# the watchdog, and the board would restart in the middle of the copy.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
port="" wifi="" name="" host="pico-sensors"
while [ $# -gt 0 ]; do
  case "$1" in
    --port) port="$2"; shift 2 ;;
    --wifi) wifi="$2"; shift 2 ;;
    --name) name="$2"; shift 2 ;;
    --hostname) host="$2"; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
if [ -z "$port" ]; then
  boards=(/dev/serial/by-id/usb-MicroPython_Board_in_FS_mode_*)
  [ -e "${boards[0]}" ] || { echo "no MicroPython board on USB" >&2; exit 1; }
  [ ${#boards[@]} -eq 1 ] || { echo "several boards on USB; pick one with --port" >&2; exit 1; }
  port="${boards[0]}"
fi
cd "$here/pico"
if [ -n "$wifi" ]; then
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  ssid="$(nmcli -g 802-11-wireless.ssid connection show "$wifi")"
  psk="$(nmcli -s -g 802-11-wireless-security.psk connection show "$wifi")"
  (umask 077; python3 -I -c 'import json,sys; json.dump({"ssid": sys.argv[1], "password": sys.argv[2], "name": sys.argv[3], "hostname": sys.argv[4]}, open(sys.argv[5], "w"))' \
    "$ssid" "$psk" "$name" "$host" "$tmp/config.json")
  mpremote connect "$port" resume cp "$tmp/config.json" :config.json
fi
mpremote connect "$port" resume cp font5x7.py vl53l1x.py max30101.py main.py : \
  + resume exec "import machine; machine.reset()" || true   # the reset drops the USB link
echo "deployed; the Pico restarts and joins Wi-Fi in a few seconds"
