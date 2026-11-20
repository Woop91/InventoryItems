#!/usr/bin/env bash
# Install the persistent dashboard. Optional argument: saved /data.json to import.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
app="$HOME/.local/share/pico-sensors/air-app"
mkdir -p "$app" "$HOME/.config/systemd/user"
cp "$here/desk/light_dash.py" "$here/desk/light_dash.html" "$app/"
if [ $# -gt 0 ]; then
  python3 -I "$app/light_dash.py" --import-json "$1"
fi
# Stop the old transient unit before installing its persistent replacement.
systemctl --user stop pico-lipo-dash.service || true
cp "$here/desk/pico-lipo-dash.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now pico-lipo-dash.service
echo 'Air dashboard: http://127.0.0.1:8772/'
