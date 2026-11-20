# Pico W sensor box

A Raspberry Pi Pico W on a Pimoroni Pico Breakout Garden Base reads Pimoroni breakouts, buzzes when the air gets stuffy, scrolls the readings across a green LED matrix and serves them over Wi-Fi. A small service on the workstation keeps the history and shows it on a dashboard.

The dashboard also offers **All** saved history and reports the stored date range
and recording gaps. Data remains in SQLite across restarts; missing intervals
cannot be recovered from the devices. Latest readings are restored after a
service restart with their original age, so an offline box cannot appear fresh.
Room selection is resolved before requesting history, and selecting an offline
room clears the previous room's current values.

The [Pico LiPo dashboard](../pico-lipo-light/README.md) separately records the
air box's LoRa readings relayed by Desk. Keep this workstation connected to the
sensor LAN even when its internet connection uses Ethernet. On NetworkManager,
the sensor Wi-Fi profile should autoconnect with a high priority and
`connection.autoconnect-retries 0` (retry indefinitely).

| Part | I2C address | What it gives |
|---|---|---|
| SCD41 CO2 sensor | 0x62 | CO2 (ppm), temperature, humidity |
| VL53L1X time-of-flight sensor | 0x29 | distance to whatever is in front of it, up to about 4 m |
| MAX30101 pulse sensor | 0x57 | heart rate while a fingertip rests on it (the one on hand is faulty, see below) |
| LTP305 LED Dot Matrix Breakout, green | 0x61 | two 5x7 characters |
| Haptic Bzzz (DRV2605L) | 0x5A | three buzzes when CO2 passes 1200 ppm |

The breakouts sit on the Garden base's I2C bus (SDA GP4, SCL GP5). The firmware is Pimoroni's MicroPython build for the Pico W (`picow v1.20.6`), which carries the SCD41 and dot-matrix drivers; `vl53l1x.py` and `max30101.py` here cover the other two.

## What the matrix shows

- Normally a scrolling line: `CO2 928   78.6°F   37%   45cm`.
- With a fingertip on the MAX30101: a pulsing heart while it measures, then the heart rate as two digits. The right decimal point flashes, and the left one means "plus 100". The heart rate is a hobby estimate, not a medical reading.
- When CO2 is over 1200 ppm the line starts with `OPEN WINDOW`, and the haptic board buzzes three times: at most once every 30 minutes, never between 10 PM and 7 AM. Set `"co2_buzz": false` in `config.json` to keep it quiet, or change `co2_alert_ppm`.
- It dims from 10 PM to 7 AM Eastern.

## Pico API (port 80)

- `GET /data.json`: `co2_ppm`, `temp_c`, `temp_f`, `humidity_pct`, `distance_mm` (null when nothing is in range), `finger`, `bpm`, `rssi`, `uptime_s`, and `parts` (which breakouts are working).
- `GET /`: the same readings as a small page.
- `GET /buzz`: buzz the haptic board now, to test it.
- `GET /scan`: every address answering on the I2C bus, to check wiring over Wi-Fi.

A breakout that is missing or stops answering is skipped, and the Pico looks for it again every 30 seconds. A hardware watchdog restarts the board if the program ever freezes.

## Dashboard

`desk/pico_sensors_desk.py` runs as a user service on the workstation. It polls every sensor box every 5 seconds, stores each reading in `~/.local/share/pico-sensors/readings.sqlite` and serves the dashboard at http://127.0.0.1:8771/. It is published to the tailnet at https://509dds-ai.tail36b40f.ts.net:8452/.

The dashboard has a card for each room side by side (CO2 with a fresh/stuffy rating, temperature, humidity, online or not). Pick a room to see its CO2 meter, tiles for temperature in °F, humidity, distance and heart rate, and charts for the last hour, 6 hours, day, week or 30 days. It also has a data table, a CSV download of every room, and a light/dark switch. Times are Eastern.

Two boxes run today:

| Box | Pico W MAC | Parts |
|---|---|---|
| Desk | 28:cd:c1:08:ef:1a | SCD41, LTP305 matrix, Haptic Bzzz |
| Room 2 | 28:cd:c1:0c:bb:4e | SCD41 (the generic purple module) |

Boxes are known by their Wi-Fi MAC address. The service scans the local network every 10 minutes, and straight away when a box stops answering, so a box with a new DHCP address is found again and a new box shows up on its own. Names live in `~/.config/pico-sensors/desk.json`; edit one and restart the service (`systemctl --user restart pico-sensors-desk`) to rename a room.

## Set up

```sh
# A new box: copy the program, plus the Wi-Fi password from this machine's saved
# 2.4 GHz network, a room name and a hostname
tools/deploy_pico.sh --wifi SturdyToast --name "Room 2" --hostname pico-sensors-2
# later updates: tools/deploy_pico.sh   (--port PORT when more than one Pico is on USB)

# Workstation: install the service, then publish it to the tailnet
tools/install_desk.sh
tailscale serve --bg --https=8452 http://127.0.0.1:8771
```

`config.json` on the Pico holds the Wi-Fi name and password and never goes into this repository. It also takes `name`, `hostname`, `brightness`, `night_brightness`, `night_start`, `night_end`, `temp_offset_f`, `co2_alert_ppm` and `co2_buzz`.

## Working on the Pico over USB

Use `mpremote connect <port> resume ...`. Without `resume`, mpremote soft-resets the board, which stops the timer that feeds the watchdog, and the Pico restarts about 8 seconds later. Ctrl-C at the REPL stops the program and keeps the watchdog fed until the next reset.

Unplug the USB cable before adding or removing breakouts. Plugging them in while the board is running can lock up the I2C bus.

A breakout must sit with its `2-6V` pin on the base's `2-6V`. One in backwards holds the clock line (GP5) and the slot's INT line (GP3) low, and then nothing on the bus answers, the other breakouts included. Unplug USB and turn it round.

## Notes from setting it up

- The MAX30101 on hand stopped working on Nov 18, 2026 after a while plugged in backwards: in either orientation it holds the clock line low. It is marked faulty in the inventory; the code still supports a replacement (Pimoroni PIM438).
- The SCD41 reads a few degrees warm when it sits on the base next to the Pico and the matrix (84 °F against about 78 °F on its own). Set `temp_offset_f` in `config.json`, for example `-5.0`, or move it out on a Qwiic cable.
- The Waveshare Pico-BLE HAT can't share this stack. Its connection-status pin is GP15, the same pin as the Pico-LoRa-SX126X's reset. Its UART can also be jumpered onto GP4/GP5, the Garden base's I2C pins. The Pico W's own Bluetooth makes it unnecessary.
- The Waveshare Pico-LoRa-SX126X uses GP2, GP3, GP10-GP12, GP15, GP20 and GP26, which don't clash with the Garden base's I2C. It answers on SPI but isn't used here. It talks only to other LoRa radios, such as the RAK4631 on the workstation, not to Wi-Fi.
