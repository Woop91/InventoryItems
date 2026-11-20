# Pico LiPo air dashboard

The desk dashboard at <http://127.0.0.1:8772/> records Pico LiPo air readings in
`~/.local/share/pico-sensors/air-readings.sqlite`. Data survives service restarts;
charts cover 10 minutes through 30 days or all saved history, and CSV exports every
raw sample. Charts average large ranges and leave gaps for unrecorded intervals.

It reads `DATA {json}` USB serial lines when the air box is attached. Without USB,
it records fresh `lipo` LoRa beacons received by the Desk Pico W and exposed by the
[room service](../pico-sensors/README.md). Relay timestamps account for both the
Desk reading's age and the beacon's age; repeated polls of one beacon do not create
new samples. Stale relays are not recorded. USB takes precedence while fresh.

The current radio firmware broadcasts CO2, one temperature/humidity pair, pressure,
VOC resistance and three gas resistances. Separate BME688/AHT10 temperature and
humidity readings require USB; missing channels are shown as unavailable. The
collector also understands optional radio keys `bt`, `bh`, `at`, `ah` for future
firmware carrying those channels. Do not substitute an arbitrary USB board: the
default USB ID belongs specifically to the Pico LiPo air box.

Install with `bash projects/pico-lipo-light/tools/install_desk.sh`. Python 3 and
pyserial are required. To preserve an old dashboard's in-memory readings, save its
`/data.json` before stopping it and pass that JSON file to the installer. Import is
idempotent. The installed systemd user service starts on login and restarts on
failure. Application files live outside worktrees in `~/.local/share/pico-sensors/air-app/`.

Environment overrides: `LIGHT_DASH_PORT`, `LIGHT_DASH_DEVICE`, `LIGHT_DASH_DB`,
`LIGHT_DASH_ROOM_API` (default `http://127.0.0.1:8771/api/latest`).

When USB is present, the message form sends from Pico LiPo. With the relay it sends
from Desk to Pico LiPo; the button names that direction. Queued means submitted,
not an acknowledgement from the remote box.
