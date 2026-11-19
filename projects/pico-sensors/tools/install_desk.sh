#!/usr/bin/env bash
# Install or update the desk service and its dashboard as a user service.
#   tools/install_desk.sh
# Boxes on the local network are found by themselves; names live in
# ~/.config/pico-sensors/desk.json ("boxes": [{"mac": ..., "name": ..., "host": ...}]).
# Then publish it to your tailnet (HTTPS, tailnet only):
#   tailscale serve --bg --https=8452 http://127.0.0.1:8771
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
app="$HOME/.local/share/pico-sensors/app"
mkdir -p "$app" "$HOME/.config/pico-sensors" "$HOME/.config/systemd/user"
cp "$here/desk/pico_sensors_desk.py" "$here/desk/dashboard.html" "$app/"
cp "$here/desk/pico-sensors-desk.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable pico-sensors-desk >/dev/null
systemctl --user restart pico-sensors-desk
echo "dashboard: http://127.0.0.1:8771/"
