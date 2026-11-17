# Electronics Product Inventory

Personal inventory of **387 products** — 191 from Adafruit, 132 from AliExpress, 39 from Pimoroni, 1 each from Waveshare, SparkFun, Mouser, Amazon, Orbtronic, Battery Junction, Voltaplex and Home Depot, 14 photographed parts whose store isn't recorded yet, and the bench gear (Riden RD6012 power supply, Hantek DSO2D10 oscilloscope and the TP-Link USB Wi-Fi adapter plugged into it), store not recorded either. **50 parts are marked as in use**, with my own photos.

> Open **index.html** in a browser for a visual catalog: every product with its picture, grouped by category (or store), with search, sorting and filters.

---

## Complete Beginner's Guide (Start Here)

If you've never done anything like this before, this section walks you through everything step by step. No experience needed.

### What is this project?

This is a personal catalog of electronics parts. It includes:

- **A visual catalog** (`index.html`) -- a web page you open in your browser that shows all your parts with pictures, search, and filters. This is the main thing most people will use.
- **A data file** (`products.json`) -- the raw list of all products stored in a format computers can read.
- **Pictures** (`images/`) -- a saved picture of every product, so the catalog shows images even offline.
- **Python scripts** (`scraper.py`, `generate_products.py`, `add_pimoroni.py`, `add_purchase_pdfs.py`, `fetch_product_images.py`, `build_catalog.py`) -- programs that fetch product info, add products and rebuild the catalog. You only need these if you want to add or refresh products.

### What files do what?

| File | What it is | Who needs it |
|------|-----------|--------------|
| `index.html` | The visual catalog you view in a browser | Everyone |
| `products.json` | Raw product data in a structured format | Advanced users |
| `purchase_history.csv` | Spreadsheet of past Adafruit orders | Reference only |
| `data/purchase_pdfs.json` | Products read from saved AliExpress (and other store) order PDFs | Reference only |
| `images/` | Product pictures used by the catalog | Everyone (keep next to `index.html`) |
| `scraper.py` | Script that fetches product info from Adafruit | Only if updating products |
| `generate_products.py` | Script that builds `products.json` from the Adafruit order CSV | Only if updating products |
| `add_pimoroni.py` | Script that adds Pimoroni products | Only if updating products |
| `add_purchase_pdfs.py` | Script that adds the order-PDF products to `products.json` | Only if updating products |
| `fetch_product_images.py` | Script that downloads a picture for any product that lacks a local one | Only if updating products |
| `build_catalog.py` | Script that builds `index.html` (and, with `--readme`, the product tables below) | Only if updating products |
| `data/parts_in_use.json` | The parts I'm currently using, with my photos (`images/my-photos/`) | Reference only |
| `mark_in_use.py` | Script that applies `data/parts_in_use.json` to `products.json` | Only if updating products |

---

### Step 1: Download the project to your computer

You're probably reading this on GitHub right now. You need to download the files to your own computer first.

**Option A -- Download as a ZIP (easiest, no software needed):**

1. On the GitHub page for this project, look for the green **"Code"** button near the top right.
2. Click it and choose **"Download ZIP"**.
3. A `.zip` file will download. Find it in your Downloads folder.
4. **Extract / unzip** the file:
   - **Windows:** Right-click the `.zip` file and choose **"Extract All..."**, then click **Extract**.
   - **Mac:** Double-click the `.zip` file -- it unzips automatically.
5. You now have a folder called something like `InventoryItems-main`. Open it -- you should see `index.html`, `products.json`, and the other files.

**Option B -- Clone with Git (for users who have Git installed):**

If you have Git installed (if you don't know what Git is, use Option A above):

1. Open a terminal (see "What is a terminal?" below).
2. Type: `git clone https://github.com/YOUR_USERNAME/InventoryItems.git`
3. Press **Enter**. The project will download into a new folder called `InventoryItems`.

---

### Step 2: View the product catalog (no coding required)

This is the main feature -- a visual page showing all your electronics parts.

1. Open the project folder you downloaded in Step 1.
2. Find the file called **`index.html`**.
3. **Double-click** it. It should open in your web browser (Chrome, Firefox, Safari, or Edge).
4. If it doesn't open automatically: **right-click** the file, choose **"Open with"**, and pick any web browser.

That's it! You should now see a light page with product cards grouped by category, each with a picture.

**Troubleshooting:** If you see raw code instead of a nice page, you accidentally opened the file in a text editor. Right-click the file and specifically choose a browser like Chrome or Firefox.

---

### Step 3: Use the catalog (searching, filtering, browsing)

Once the page is open in your browser:

**Search for a product:**
1. Click the search box at the top (it says "Search name, specs, chip, store…").
2. Type what you're looking for -- for example, `sensor` or `ESP32` or `LED`.
3. The page instantly hides everything that doesn't match. The counter on the right (e.g., "Showing 15 of 384") tells you how many results you have.
4. To clear the search: delete the text, or click the small X in the search box.

**Arrange by category:**
- Products are grouped by category (Sensor, Motor/Actuator, Power, ...). Click a category heading to fold it away; **Collapse all** / **Expand all** folds every group.
- **Group by** switches between Category, Store, or one big grid. **Groups** orders them A–Z or by most items. **Sort** orders products inside each group by name, price or store.
- Click a coloured category chip to hide or show that category. Click a store chip (Adafruit, AliExpress, ...) to show only that store; click it again to undo.
- **Compact view** shows smaller cards with just the picture, name and price.
- **Using now** at the top lists the parts I'm working with, each with my own photos (click one to enlarge). Tick **Only parts I'm using** to hide everything else.
- Your choices are remembered the next time you open the page in the same browser.
- Filters combine with search -- you can search for "sensor" within just AliExpress products.

**Use your browser's built-in find:**
- Press **Ctrl+F** (Windows/Linux) or **Cmd+F** (Mac) to open your browser's find bar.
- Type any word and the browser will highlight and jump to every match on the page.

**View product details:**
- Click a product's **picture** to see it larger (click again or press Esc to close).
- Click **"Specs"** on any card to expand and read the specifications.
- Click **"Product page"** or **"Guide"** (when available) to open the store page or a tutorial in a new tab.
- Products imported from order PDFs show which PDF they came from.

**Scroll through products:**
- **Mouse:** Scroll wheel, or drag the scrollbar on the right.
- **Trackpad:** Swipe up/down with two fingers.
- **Keyboard:** Press **Space** to scroll down, **Shift+Space** to scroll up.

---

### Step 4 (Optional, Advanced): Run the Python scripts to update products

You only need this if you want to re-fetch product data from supplier websites or rebuild the catalog. If you just want to view your inventory, you can stop at Step 3.

#### What is Python?

Python is a programming language. The `.py` files in this project are Python programs. To run them, you need Python installed on your computer.

#### What is a terminal?

A terminal (also called "command prompt" or "command line") is a text-based window where you type commands. It looks like a black or white window with a blinking cursor.

- **Windows:** Press the **Windows key**, type `cmd`, and press Enter. Or search for "Command Prompt" or "PowerShell".
- **Mac:** Open **Finder**, go to **Applications > Utilities > Terminal**. Or press **Cmd+Space**, type `Terminal`, and press Enter.
- **Linux:** Press **Ctrl+Alt+T**, or find "Terminal" in your applications menu.

#### Install Python

1. Check if Python is already installed: open a terminal and type `python --version` (or `python3 --version`) and press Enter.
   - If you see something like `Python 3.10.4`, you're good -- skip to the next section.
   - If you get an error like "not recognized" or "command not found", you need to install it.
2. Go to **https://www.python.org** in your browser.
3. Click the big **"Download Python"** button.
4. Run the installer.
   - **Windows users: Check the box that says "Add Python to PATH"** before clicking Install. This is important!
5. After installation, close and reopen your terminal, then try `python --version` again.

#### Install required libraries

The scripts need a few additional libraries. In your terminal, type:

```
pip install requests beautifulsoup4 pillow
```

Press Enter. You should see it download and install successfully. If `pip` doesn't work, try `pip3` instead.

#### Navigate to the project folder

In your terminal, you need to go to the folder where you downloaded the project:

```
cd /path/to/InventoryItems
```

Replace `/path/to/InventoryItems` with the actual location. For example:
- **Windows:** `cd C:\Users\YourName\Downloads\InventoryItems-main`
- **Mac:** `cd ~/Downloads/InventoryItems-main`

**Tip:** On most systems, you can type `cd ` (with a space) and then **drag and drop** the folder onto the terminal window to paste its path.

#### Run the scraper

Now you can run the scripts:

```
python scraper.py
```

This fetches the latest product information from Adafruit and updates `products.json` and `index.html`. It takes a few minutes because it visits each product page and waits between requests to be polite to the server.

To force a full refresh of all products (even ones already scraped):

```
python scraper.py --force
```

After it finishes, refresh `index.html` in your browser (press **F5** or **Ctrl+R**) to see the updated catalog.

---

## Quick Links

| File | Description |
|------|-------------|
| [`index.html`](index.html) | Visual product catalog (open in browser) |
| [`products.json`](products.json) | Machine-readable product data |
| [`purchase_history.csv`](purchase_history.csv) | Adafruit order history |
| [`scraper.py`](scraper.py) | Scraper to fetch live data from adafruit.com |
| [`data/purchase_pdfs.json`](data/purchase_pdfs.json) | Products read from saved order PDFs |
| [`build_catalog.py`](build_catalog.py) | Builds `index.html` and the README product tables |

## How to Update (Quick Reference)

```bash
pip install requests beautifulsoup4 pillow
python scraper.py              # scrape Adafruit products
python scraper.py --force      # re-scrape everything
python add_purchase_pdfs.py    # merge data/purchase_pdfs.json into products.json
python fetch_product_images.py # download pictures for products without one
python mark_in_use.py          # mark the parts in data/parts_in_use.json as in use
python build_catalog.py --readme  # rebuild index.html and the README tables
```

---

## Parts I'm using

51 parts, each with my own photos in `images/my-photos/`.

| Product | Category | Store | My photos |
|---------|----------|-------|----------:|
| Pico Breakout Garden Base | Accessory | Pimoroni | 7 |
| pHAT Stack - Solder Yourself Kit | Accessory | Pimoroni | 2 |
| 01Studio PiHAT Expansion Board for Raspberry Pi (with OLED) | Breakout Board | AliExpress | 3 |
| Adafruit DRV2605L Haptic Motor Controller   STEMMA QT / Qwiic | Breakout Board | Adafruit | 1 |
| Adafruit DS3502 I2C Digital 10K Potentiometer Breakout | Breakout Board | Adafruit | 2 |
| Adafruit I2C Stemma QT Rotary Encoder Breakout with NeoPixel | Breakout Board | Adafruit | 2 |
| Adafruit Infineon Trust M Breakout Board   STEMMA QT / Qwiic | Breakout Board | Adafruit | 2 |
| Adafruit Qwiic / Stemma QT 5 Port Hub | Breakout Board | Adafruit | 2 |
| Button SHIM | Breakout Board | Pimoroni | 1 |
| DRV8830 DC Motor Driver Breakout | Breakout Board | Pimoroni | 3 |
| HT0740 40V / 10A Switch Breakout | Breakout Board | Pimoroni | 4 |
| IO Expander Breakout | Breakout Board | Pimoroni | 5 |
| Pimoroni Haptic Bzzz Breakout (DRV2605L) | Breakout Board | Store not recorded | 3 |
| RV3028 Real-Time Clock (RTC) Breakout | Breakout Board | Pimoroni | 2 |
| SparkFun Qwiic pHAT v2.0 for Raspberry Pi   STEMMA QT / Qwiic | Breakout Board | Adafruit | 2 |
| Breakout Garden to STEMMA QT / Qwiic Adapter | Cable/Connector | Pimoroni | 6 |
| GD25Q16   2MB SPI Flash in 8 Pin SOIC package | Component | Adafruit | 6 |
| 0.91" 128x32 OLED Display Module (SSD1306, I2C, White) | Display | AliExpress | 3 |
| 1602 16x2 Character LCD with PCF8574 I2C Backpack (blue) | Display | Store not recorded | 3 |
| Adafruit RGB Matrix HAT + RTC for Raspberry Pi | Display | Store not recorded | 3 |
| LED Dot Matrix Breakout - Green | Display | Pimoroni | 3 |
| P3 RGB LED Matrix Panel, 64x32, 192x96mm (SMD2121) | Display | AliExpress | 1 |
| Scroll pHAT HD - Yellow | Display | Pimoroni | 2 |
| Waveshare 10.4inch QLED Quantum Dot Display, Capacitive Touch, 1600x720, HDMI | Display | Waveshare | 3 |
| Adafruit RGB Matrix FeatherWing | FeatherWing | Store not recorded | 3 |
| Adafruit QT Py   SAMD21 Dev Board with STEMMA QT | Microcontroller | Adafruit | 7 |
| Adafruit QT Py ESP32 S2 WiFi Dev Board with uFL Antenna Port | Microcontroller | Adafruit | 9 |
| Adafruit Trinkey QT2040   RP2040 USB Key with Stemma QT | Microcontroller | Adafruit | 7 |
| Pimoroni Pico LiPo - 16MB | Microcontroller | Pimoroni | 3 |
| Raspberry Pi 4 Model B | Microcontroller | Store not recorded | 2 |
| Raspberry Pi Pico W | Microcontroller | Store not recorded | 3 |
| Waveshare RP2040-PiZero | Microcontroller | Store not recorded | 2 |
| Waveshare RP2040-Plus | Microcontroller | Store not recorded | 2 |
| YD-RP2040 RP2040 Development Board (black) | Microcontroller | Store not recorded | 1 |
| 8mm Coin Vibration Motor 3V (2 pcs) | Motor/Actuator | AliExpress | 1 |
| AHT10 Temperature and Humidity Sensor Module (I2C) | Sensor | AliExpress | 5 |
| Adafruit AHT20   Temperature & Humidity Sensor Breakout Board | Sensor | Adafruit | 2 |
| Adafruit BH1750 Light Sensor   STEMMA QT / Qwiic | Sensor | Adafruit | 2 |
| Adafruit LPS35HW Water Resistant Pressure Sensor - STEMMA QT | Sensor | Pimoroni | 2 |
| Adafruit VL53L1X Time of Flight Distance Sensor (STEMMA QT) | Sensor | Store not recorded | 2 |
| BME688 4-in-1 Air Quality Breakout (Gas, Temperature, Pressure, Humidity) | Sensor | Pimoroni | 2 |
| CJMCU-3216 AP3216C Light and Proximity Sensor | Sensor | Store not recorded | 5 |
| Generic SCD41 CO2 Sensor Module (purple) | Sensor | AliExpress | 4 |
| INA219  High Side DC Current Sensor Breakout   26V ±3.2A Max | Sensor | Adafruit | 2 |
| MAX30101 Breakout - Heart Rate, Oximeter, Smoke Sensor | Sensor | Pimoroni | 1 |
| MICS6814 3-in-1 Gas Sensor Breakout (CO, NO2, NH3) | Sensor | Pimoroni | 2 |
| SCD41 CO2 Sensor Breakout (Carbon Dioxide / Temperature / Humidity) | Sensor | Pimoroni | 3 |
| VL53L1X Time of Flight (ToF) Sensor Breakout | Sensor | Pimoroni | 2 |
| Waveshare Pico-BLE | Wireless/RF | Store not recorded | 3 |
| Waveshare Pico-CAN-B | Wireless/RF | Store not recorded | 3 |
| Waveshare Pico-LoRa-SX126X | Wireless/RF | Store not recorded | 1 |

---

## Categories by Source

### Adafruit (191 products)

- [Microcontroller](#adafruit---microcontroller) (10)
- [Sensor](#adafruit---sensor) (9)
- [Display](#adafruit---display) (8)
- [LED](#adafruit---led) (14)
- [Breakout Board](#adafruit---breakout-board) (18)
- [FeatherWing](#adafruit---featherwing) (12)
- [Component](#adafruit---component) (27)
- [Cable/Connector](#adafruit---cableconnector) (25)
- [Prototyping](#adafruit---prototyping) (20)
- [Power](#adafruit---power) (2)
- [Kit](#adafruit---kit) (2)
- [Tool](#adafruit---tool) (12)
- [Enclosure](#adafruit---enclosure) (2)
- [Storage](#adafruit---storage) (4)
- [Accessory](#adafruit---accessory) (23)
- [Book/Subscription](#adafruit---booksubscription) (3)

### Pimoroni (39 products)

- [Microcontroller](#pimoroni---microcontroller) (1)
- [Sensor](#pimoroni---sensor) (7)
- [Display](#pimoroni---display) (5)
- [Breakout Board](#pimoroni---breakout-board) (8)
- [FeatherWing](#pimoroni---featherwing) (1)
- [Component](#pimoroni---component) (2)
- [Cable/Connector](#pimoroni---cableconnector) (3)
- [Prototyping](#pimoroni---prototyping) (2)
- [Power](#pimoroni---power) (2)
- [Tool](#pimoroni---tool) (2)
- [Accessory](#pimoroni---accessory) (6)

### Waveshare (1 products)

- [Display](#waveshare---display) (1)

### SparkFun (1 products)

- [Breakout Board](#sparkfun---breakout-board) (1)

### Mouser (1 products)

- [Sensor](#mouser---sensor) (1)

### AliExpress (132 products)

- [Microcontroller](#aliexpress---microcontroller) (8)
- [Sensor](#aliexpress---sensor) (21)
- [Display](#aliexpress---display) (6)
- [LED](#aliexpress---led) (9)
- [Breakout Board](#aliexpress---breakout-board) (2)
- [Motor/Actuator](#aliexpress---motoractuator) (16)
- [Motor Driver/ESC](#aliexpress---motor-driveresc) (10)
- [Switch/Button](#aliexpress---switchbutton) (9)
- [Audio](#aliexpress---audio) (5)
- [Wireless/RF](#aliexpress---wirelessrf) (6)
- [Component](#aliexpress---component) (10)
- [Cable/Connector](#aliexpress---cableconnector) (5)
- [Power](#aliexpress---power) (15)
- [Battery](#aliexpress---battery) (4)
- [Kit](#aliexpress---kit) (2)
- [Tool](#aliexpress---tool) (4)

### Amazon (1 products)

- [Microcontroller](#amazon---microcontroller) (1)

### Orbtronic (1 products)

- [Battery](#orbtronic---battery) (1)

### Battery Junction (1 products)

- [Battery](#battery-junction---battery) (1)

### Voltaplex (1 products)

- [Battery](#voltaplex---battery) (1)

### Home Depot (1 products)

- [Accessory](#home-depot---accessory) (1)

### Store not recorded (17 products)

- [Microcontroller](#store-not-recorded---microcontroller) (5)
- [Sensor](#store-not-recorded---sensor) (2)
- [Display](#store-not-recorded---display) (2)
- [Breakout Board](#store-not-recorded---breakout-board) (1)
- [FeatherWing](#store-not-recorded---featherwing) (1)
- [Wireless/RF](#store-not-recorded---wirelessrf) (4)
- [Tool](#store-not-recorded---tool) (2)

---

# Adafruit Products

## Adafruit - Microcontroller

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 3176 | Adafruit Feather M0 RFM69HCW Packet Radio   868 or 915 MHz | 2 | $24.95 | [Product](https://www.adafruit.com/product/3176) · [Guide](https://learn.adafruit.com/adafruit-feather-m0-radio-with-rfm69-packet-radio) |
| 3333 | Circuit Playground Express | 4 | $24.95 | [Product](https://www.adafruit.com/product/3333) · [Guide](https://learn.adafruit.com/adafruit-circuit-playground-express) |
| 3500 | Adafruit Trinket M0   for use with CircuitPython & Arduino IDE | 1 | $8.95 | [Product](https://www.adafruit.com/product/3500) · [Guide](https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino) |
| 3505 | Adafruit METRO M0 Express   designed for CircuitPython | 1 | $24.95 | [Product](https://www.adafruit.com/product/3505) · [Guide](https://learn.adafruit.com/adafruit-metro-m0-express) |
| 4600 | Adafruit QT Py   SAMD21 Dev Board with STEMMA QT | 1 | $7.50 | [Product](https://www.adafruit.com/product/4600) · [Guide](https://learn.adafruit.com/adafruit-qt-py) |
| 4884 | Adafruit Feather RP2040 | 1 | $11.95 | [Product](https://www.adafruit.com/product/4884) · [Guide](https://learn.adafruit.com/adafruit-feather-rp2040-pico) |
| 50 | Adafruit METRO 328 Fully Assembled   Arduino IDE compatible | 1 | $17.50 | [Product](https://www.adafruit.com/product/50) · [Guide](https://learn.adafruit.com/adafruit-metro) |
| 5056 | Adafruit Trinkey QT2040   RP2040 USB Key with Stemma QT | 1 | $7.50 | [Product](https://www.adafruit.com/product/5056) · [Guide](https://learn.adafruit.com/adafruit-trinkey-qt2040) |
| 5302 | Adafruit KB2040   RP2040 Kee Boar Driver | 3 | $8.95 | [Product](https://www.adafruit.com/product/5302) · [Guide](https://learn.adafruit.com/adafruit-kb2040) |
| 5348 | Adafruit QT Py ESP32 S2 WiFi Dev Board with uFL Antenna Port | 1 | $12.50 | [Product](https://www.adafruit.com/product/5348) · [Guide](https://learn.adafruit.com/adafruit-qt-py-esp32-s2) |

## Adafruit - Sensor

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 157 | IR (Infrared) Receiver Sensor | 1 | $1.95 | [Product](https://www.adafruit.com/product/157) · [Guide](https://learn.adafruit.com/ir-sensor) |
| 1766 | Fast Vibration Sensor Switch (Easy to trigger) | 2 | $0.95 | [Product](https://www.adafruit.com/product/1766) |
| 2384 | Medium Vibration Sensor Switch | 2 | $0.95 | [Product](https://www.adafruit.com/product/2384) |
| 4081 | Flat Vibration Switch   Breadboard friendly | 4 | $0.95 | [Product](https://www.adafruit.com/product/4081) |
| 4566 | Adafruit AHT20   Temperature & Humidity Sensor Breakout Board | 1 | $4.50 | [Product](https://www.adafruit.com/product/4566) · [Guide](https://learn.adafruit.com/adafruit-aht20) |
| 4582 | Finger Pulse Oximeter with Bluetooth LE | 1 | $49.95 | [Product](https://www.adafruit.com/product/4582) · [Guide](https://learn.adafruit.com/bluetooth-le-finger-pulse-oximeter) |
| 4681 | Adafruit BH1750 Light Sensor   STEMMA QT / Qwiic | 1 | $4.50 | [Product](https://www.adafruit.com/product/4681) · [Guide](https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor) |
| 4871 | Breadboard friendly Mini PIR Motion Sensor with 3 Pin Header | 3 | $3.95 | [Product](https://www.adafruit.com/product/4871) · [Guide](https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor) |
| 904 | INA219  High Side DC Current Sensor Breakout   26V ±3.2A Max | 1 | $9.95 | [Product](https://www.adafruit.com/product/904) · [Guide](https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout) |

## Adafruit - Display

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 1048 | Adafruit 1.2" 8x8 LED Matrix Backpack | 3 | $6.00 | [Product](https://www.adafruit.com/product/1048) · [Guide](https://learn.adafruit.com/adafruit-led-backpack) |
| 1265 | Yellow 7 segment clock display   1.2" digit height | 1 | $7.50 | [Product](https://www.adafruit.com/product/1265) · [Guide](https://learn.adafruit.com/adafruit-led-backpack) |
| 1431 | OLED Breakout Board   16 bit Color 1.5" w/microSD holder | 1 | $39.95 | [Product](https://www.adafruit.com/product/1431) · [Guide](https://learn.adafruit.com/adafruit-1-5-color-oled-breakout-board) |
| 326 | Monochrome 0.96" 128x64 OLED Graphic Display   STEMMA QT | 1 | $17.50 | [Product](https://www.adafruit.com/product/326) · [Guide](https://learn.adafruit.com/monochrome-oled-breakouts) |
| 398 | RGB backlight positive LCD 16x2   extras | 1 | $12.95 | [Product](https://www.adafruit.com/product/398) · [Guide](https://learn.adafruit.com/rgb-backlit-lcds) |
| 5036 | 64x32 RGB LED Matrix   2.5mm pitch | 1 | $34.95 | [Product](https://www.adafruit.com/product/5036) · [Guide](https://learn.adafruit.com/adafruit-matrixportal-m4) |
| 715 | Adafruit I2C Controlled   Keypad Shield Kit for 16x2 LCD | 1 | $14.95 | [Product](https://www.adafruit.com/product/715) · [Guide](https://learn.adafruit.com/adafruit-i2c-controlled-keypad-shield-for-16x2-lcd) |
| 877 | Adafruit 7 Segment LED Matrix Backpack   STEMMA QT / qwiic | 1 | $6.95 | [Product](https://www.adafruit.com/product/877) · [Guide](https://learn.adafruit.com/adafruit-led-backpack) |

## Adafruit - LED

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 1312 | Breadboard friendly RGB Smart NeoPixel   Pack of 5 | 1 | $7.95 | [Product](https://www.adafruit.com/product/1312) · [Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide) |
| 1399 | RGB 7 Segment Digit   1" Tall Digit | 2 | $14.95 | [Product](https://www.adafruit.com/product/1399) |
| 1426 | NeoPixel Stick   8 x 5050 RGB LED with Integrated Drivers | 1 | $5.95 | [Product](https://www.adafruit.com/product/1426) · [Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide) |
| 159 | Diffused RGB (tri color) LED | 1 | $2.00 | [Product](https://www.adafruit.com/product/159) |
| 1612 | NeoPixel Mini Button PCB   Pack of 5 | 1 | $4.95 | [Product](https://www.adafruit.com/product/1612) · [Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide) |
| 1623 | Small 1.2" 8x8 Ultra Bright Pure Green LED Matrix | 1 | $4.95 | [Product](https://www.adafruit.com/product/1623) · [Guide](https://learn.adafruit.com/adafruit-led-backpack) |
| 1655 | NeoPixel 5050 RGB LED with Integrated Driver Chip   10 Pack | 1 | $4.50 | [Product](https://www.adafruit.com/product/1655) · [Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide) |
| 1734 | NeoPixel Diffused 8mm Through Hole LED   5 Pack | 1 | $4.95 | [Product](https://www.adafruit.com/product/1734) · [Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide) |
| 2530 | 3W RGB LED   Common Anode | 1 | $2.95 | [Product](https://www.adafruit.com/product/2530) |
| 2739 | Diffused Rectangular 5mm RGB LEDs   Pack of 10 | 1 | $5.95 | [Product](https://www.adafruit.com/product/2739) |
| 4042 | Diffused Red and Green Indicator LED   18mm Round | 9 | $1.50 | [Product](https://www.adafruit.com/product/4042) |
| 4203 | Diffused 5mm LED Pack   5 LEDs each in 5 Colors   25 Pack | 1 | $4.95 | [Product](https://www.adafruit.com/product/4203) |
| 455 | Small 1.2" 8x8 Ultra Bright Red LED Matrix | 3 | $3.95 | [Product](https://www.adafruit.com/product/455) · [Guide](https://learn.adafruit.com/adafruit-led-backpack) |
| 860 | Miniature 8x8 Yellow LED Matrix | 1 | $3.95 | [Product](https://www.adafruit.com/product/860) · [Guide](https://learn.adafruit.com/adafruit-led-backpack) |

## Adafruit - Breakout Board

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 1616 | Adafruit Trellis Monochrome Driver PCB for 4x4 Keypad & 3mm LEDs | 1 | $9.95 | [Product](https://www.adafruit.com/product/1616) · [Guide](https://learn.adafruit.com/adafruit-trellis-diy-open-source-led-keypad) |
| 1754 | Adafruit Assembled Pi T Cobbler Breakout for Raspberry Pi | 1 | $6.95 | [Product](https://www.adafruit.com/product/1754) · [Guide](https://learn.adafruit.com/adafruit-pi-t-cobbler) |
| 2028 | Assembled Pi T Cobbler Plus   GPIO Breakout | 2 | $7.95 | [Product](https://www.adafruit.com/product/2028) · [Guide](https://learn.adafruit.com/adafruit-pi-t-cobbler-plus) |
| 2200 | Precision LM4040 Voltage Reference Breakout   2.048V and 4.096V | 1 | $7.50 | [Product](https://www.adafruit.com/product/2200) · [Guide](https://learn.adafruit.com/adafruit-lm4040-voltage-reference-breakout) |
| 2305 | Adafruit DRV2605L Haptic Motor Controller   STEMMA QT / Qwiic | 3 | $7.95 | [Product](https://www.adafruit.com/product/2305) · [Guide](https://learn.adafruit.com/adafruit-drv2605-haptic-controller-breakout) |
| 2717 | TCA9548A I2C Multiplexer | 1 | $6.95 | [Product](https://www.adafruit.com/product/2717) · [Guide](https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout) |
| 292 | i2c / SPI character LCD backpack   STEMMA QT / Qwiic | 1 | $9.95 | [Product](https://www.adafruit.com/product/292) · [Guide](https://learn.adafruit.com/i2c-spi-lcd-backpack) |
| 3070 | Adafruit RFM69HCW Transceiver Radio Breakout   868 or 915 MHz | 2 | $9.95 | [Product](https://www.adafruit.com/product/3070) · [Guide](https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts) |
| 3954 | Adafruit NeoTrellis RGB Driver PCB for 4x4 Keypad | 2 | $12.50 | [Product](https://www.adafruit.com/product/3954) · [Guide](https://learn.adafruit.com/adafruit-neotrellis) |
| 4286 | Adafruit DS3502 I2C Digital 10K Potentiometer Breakout | 1 | $4.95 | [Product](https://www.adafruit.com/product/4286) · [Guide](https://learn.adafruit.com/ds3502-i2c-potentiometer) |
| 4351 | Adafruit Infineon Trust M Breakout Board   STEMMA QT / Qwiic | 1 | $4.95 | [Product](https://www.adafruit.com/product/4351) · [Guide](https://learn.adafruit.com/adafruit-infineon-trust-m-breakout) |
| 4886 | Adafruit AW9523 GPIO Expander and LED Driver Breakout | 1 | $4.95 | [Product](https://www.adafruit.com/product/4886) · [Guide](https://learn.adafruit.com/adafruit-aw9523-gpio-expander-and-led-driver) |
| 4991 | Adafruit I2C Stemma QT Rotary Encoder Breakout with NeoPixel | 3 | $5.95 | [Product](https://www.adafruit.com/product/4991) · [Guide](https://learn.adafruit.com/adafruit-i2c-qt-rotary-encoder) |
| 5142 | SparkFun Qwiic pHAT v2.0 for Raspberry Pi   STEMMA QT / Qwiic | 1 | $7.95 | [Product](https://www.adafruit.com/product/5142) |
| 5188 | Adafruit DS3231 Precision RTC   STEMMA QT | 1 | $13.95 | [Product](https://www.adafruit.com/product/5188) · [Guide](https://learn.adafruit.com/adafruit-ds3231-precision-rtc-breakout) |
| 5221 | Adafruit ANO Rotary Navigation Encoder Breakout PCB | 1 | $1.50 | [Product](https://www.adafruit.com/product/5221) · [Guide](https://learn.adafruit.com/adafruit-ano-rotary-navigation-encoder-breakout) |
| 5625 | Adafruit Qwiic / Stemma QT 5 Port Hub | 3 | $2.50 | [Product](https://www.adafruit.com/product/5625) |
| 757 | 4 channel I2C safe Bi directional Logic Level Converter | 1 | $3.95 | [Product](https://www.adafruit.com/product/757) · [Guide](https://learn.adafruit.com/adafruit-4-channel-adc-breakouts) |

## Adafruit - FeatherWing

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 2884 | FeatherWing Proto   Prototyping Add on For All Feather Boards | 1 | $4.95 | [Product](https://www.adafruit.com/product/2884) · [Guide](https://learn.adafruit.com/featherwing-proto-and-doubler) |
| 2900 | Adafruit FeatherWing OLED   128x32 OLED Add on For Feather | 1 | $14.95 | [Product](https://www.adafruit.com/product/2900) · [Guide](https://learn.adafruit.com/adafruit-oled-featherwing) |
| 2922 | Adalogger FeatherWing   RTC   SD Add on For All Feather Boards | 1 | $8.95 | [Product](https://www.adafruit.com/product/2922) · [Guide](https://learn.adafruit.com/adafruit-adalogger-featherwing) |
| 2926 | Assembled Terminal Block Breakout FeatherWing for all Feathers | 1 | $14.95 | [Product](https://www.adafruit.com/product/2926) · [Guide](https://learn.adafruit.com/adafruit-terminal-block-breakout-featherwing) |
| 2927 | DC Motor   Stepper FeatherWing Add on For All Feather Boards | 1 | $19.95 | [Product](https://www.adafruit.com/product/2927) · [Guide](https://learn.adafruit.com/adafruit-stepper-dc-motor-featherwing) |
| 2928 | 8 Channel PWM or Servo FeatherWing Add on For All Feather Boards | 1 | $9.95 | [Product](https://www.adafruit.com/product/2928) · [Guide](https://learn.adafruit.com/adafruit-8-channel-pwm-or-servo-featherwing) |
| 3134 | Adafruit 15x7 CharliePlex LED Matrix Display FeatherWing   Red | 1 | $9.95 | [Product](https://www.adafruit.com/product/3134) · [Guide](https://learn.adafruit.com/adafruit-15x7-7x15-charlieplex-led-matrix-display-featherwing) |
| 3152 | Adafruit 0.8" 8x16 LED Matrix FeatherWing Display   Red | 1 | $11.95 | [Product](https://www.adafruit.com/product/3152) · [Guide](https://learn.adafruit.com/adafruit-led-backpack) |
| 3988 | Adafruit Prop Maker FeatherWing | 1 | $9.95 | [Product](https://www.adafruit.com/product/3988) · [Guide](https://learn.adafruit.com/adafruit-prop-maker-featherwing) |
| 4147 | Adafruit ADXL343   ADT7410 Sensor FeatherWing | 1 | $11.95 | [Product](https://www.adafruit.com/product/4147) · [Guide](https://learn.adafruit.com/adafruit-adxl343-adt7410-sensor-featherwing) |
| 4565 | Adafruit LSM6DSOX   LIS3MDL FeatherWing   Precision 9 DoF IMU | 1 | $19.95 | [Product](https://www.adafruit.com/product/4565) · [Guide](https://learn.adafruit.com/st-9-dof-combo) |
| 4650 | Adafruit FeatherWing OLED   128x64 OLED Add on For Feather | 1 | $14.95 | [Product](https://www.adafruit.com/product/4650) · [Guide](https://learn.adafruit.com/adafruit-128x64-oled-featherwing) |

## Adafruit - Component

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 1009 | Colorful Round Tactile Button Switch Assortment   15 pack | 1 | $5.95 | [Product](https://www.adafruit.com/product/1009) |
| 1010 | Colorful 12mm Square Tactile Button Switch Assortment   15 pack | 1 | $5.95 | [Product](https://www.adafruit.com/product/1010) |
| 1074 | Configurable Spring Terminal Blocks   3 Pin 0.1" Pitch R/A   x 5 | 1 | $4.95 | [Product](https://www.adafruit.com/product/1074) |
| 1081 | Configurable Spring Terminal Blocks   3 Pin 0.1" Pitch x 5 | 1 | $4.95 | [Product](https://www.adafruit.com/product/1081) |
| 1119 | Tactile Switch Buttons (12mm square, 6mm tall) x 10 pack | 1 | $2.50 | [Product](https://www.adafruit.com/product/1119) |
| 1201 | Vibrating Mini Motor Disc | 3 | $1.95 | [Product](https://www.adafruit.com/product/1201) |
| 1536 | Buzzer 5V   Breadboard friendly | 2 | $0.95 | [Product](https://www.adafruit.com/product/1536) |
| 1611 | Silicone Elastomer 4x4 Button Keypad   for 3mm LEDs | 1 | $4.95 | [Product](https://www.adafruit.com/product/1611) · [Guide](https://learn.adafruit.com/adafruit-trellis-diy-open-source-led-keypad) |
| 1683 | On Off Power Button / Pushbutton Toggle Switch | 1 | $1.95 | [Product](https://www.adafruit.com/product/1683) |
| 1898 | Breadboard Friendly PCB Mount Mini Speaker   8 Ohm 0.2W | 2 | $1.85 | [Product](https://www.adafruit.com/product/1898) |
| 3101 | Soft Tactile Button (8mm) x 10 | 1 | $1.95 | [Product](https://www.adafruit.com/product/3101) |
| 3104 | Mini Illuminated Momentary Pushbutton   Red Power Symbol | 1 | $1.95 | [Product](https://www.adafruit.com/product/3104) |
| 356 | Breadboard trim potentiometer | 2 | $1.25 | [Product](https://www.adafruit.com/product/356) |
| 3642 | 2.1mm DC Power Jack with Slide Switch | 1 | $1.95 | [Product](https://www.adafruit.com/product/3642) |
| 373 | Breadboard friendly 2.1mm DC barrel jack | 2 | $0.95 | [Product](https://www.adafruit.com/product/373) |
| 377 | Rotary Encoder   Extras | 4 | $4.50 | [Product](https://www.adafruit.com/product/377) · [Guide](https://learn.adafruit.com/rotary-encoder) |
| 3885 | Adafruit STEMMA Speaker   Plug and Play Audio Amplifier | 1 | $5.95 | [Product](https://www.adafruit.com/product/3885) · [Guide](https://learn.adafruit.com/adafruit-stemma-speaker) |
| 4227 | Mini Oval Speaker with Short Wires   8 Ohm 1 Watt | 1 | $1.95 | [Product](https://www.adafruit.com/product/4227) |
| 4271 | Slide Potentiometer with Plastic Knob   35mm Long   10KΩ | 1 | $1.95 | [Product](https://www.adafruit.com/product/4271) |
| 453 | MAX7219CNG LED Matrix/Digit Display Driver | 1 | $12.95 | [Product](https://www.adafruit.com/product/453) |
| 4677 | Generic 64 Mbit Serial Pseudo SRAM   PSRAM   3.3V 133 MHz | 1 | $1.75 | [Product](https://www.adafruit.com/product/4677) |
| 4763 | GD25Q16   2MB SPI Flash in 8 Pin SOIC package | 2 | $1.25 | [Product](https://www.adafruit.com/product/4763) |
| 480 | Small Arcade Joystick | 1 | $14.95 | [Product](https://www.adafruit.com/product/480) |
| 5001 | ANO Directional Navigation and Scroll Wheel Rotary Encoder | 1 | $8.95 | [Product](https://www.adafruit.com/product/5001) · [Guide](https://learn.adafruit.com/ano-rotary-encoder) |
| 735 | 74LVC245   Breadboard Friendly 8 bit Logic Level Shifter | 4 | $1.50 | [Product](https://www.adafruit.com/product/735) |
| 805 | Breadboard friendly SPDT Slide Switch | 4 | $0.95 | [Product](https://www.adafruit.com/product/805) |
| 9 | High strength 'rare earth' magnet | 2 | $2.50 | [Product](https://www.adafruit.com/product/9) |

## Adafruit - Cable/Connector

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 1328 | 2.1mm DC Barrel Jack to Alligator Clips | 1 | $1.95 | [Product](https://www.adafruit.com/product/1328) |
| 1661 | uFL SMT Antenna Connector | 6 | $0.75 | [Product](https://www.adafruit.com/product/1661) |
| 1865 | Edge Launch SMA Connector for 1.6mm / 0.062" Thick PCBs | 1 | $2.50 | [Product](https://www.adafruit.com/product/1865) |
| 261 | JST PH 2 Pin Cable   Female Connector 100mm | 3 | $0.75 | [Product](https://www.adafruit.com/product/261) |
| 2888 | BNC Male Plug Terminal Block | 1 | $0.95 | [Product](https://www.adafruit.com/product/2888) |
| 2889 | BNC Female Jack Terminal Block | 1 | $0.95 | [Product](https://www.adafruit.com/product/2889) |
| 3310 | 5.5 / 2.1mm Barrel Connector   DC Power Plug | 1 | $0.95 | [Product](https://www.adafruit.com/product/3310) |
| 3786 | 2 Pin Wire Joints (3 pack) | 2 | $0.95 | [Product](https://www.adafruit.com/product/3786) |
| 3893 | STEMMA JST PH 2mm 3 Pin to Male Header Cable   200mm | 1 | $1.25 | [Product](https://www.adafruit.com/product/3893) |
| 4030 | JST PH 2mm 3 pin Plug to Color Coded Alligator Clips Cable | 1 | $1.95 | [Product](https://www.adafruit.com/product/4030) |
| 4046 | JST PH 2mm 3 Pin Socket to Color Coded Cable   200mm | 1 | $0.95 | [Product](https://www.adafruit.com/product/4046) |
| 4209 | STEMMA QT / Qwiic JST SH 4 pin to Premium Male Headers Cable | 6 | $0.95 | [Product](https://www.adafruit.com/product/4209) |
| 4210 | STEMMA QT / Qwiic JST SH 4 pin Cable   100mm Long | 5 | $0.95 | [Product](https://www.adafruit.com/product/4210) |
| 4287 | 3.5mm / 1.1mm to 5.5mm / 2.1mm DC Jack Adapter | 1 | $1.50 | [Product](https://www.adafruit.com/product/4287) |
| 4397 | STEMMA QT / Qwiic JST SH 4 pin Cable with Premium Female Sockets | 1 | $0.95 | [Product](https://www.adafruit.com/product/4397) |
| 4398 | JST SH 4 pin Cable with Alligator Clips   STEMMA QT / Qwiic | 1 | $2.95 | [Product](https://www.adafruit.com/product/4398) |
| 4399 | STEMMA QT / Qwiic JST SH 4 Pin Cable   50mm Long | 5 | $0.95 | [Product](https://www.adafruit.com/product/4399) |
| 4401 | STEMMA QT / Qwiic JST SH 4 Pin Cable   200mm Long | 3 | $0.95 | [Product](https://www.adafruit.com/product/4401) |
| 4483 | 5 pin JST ESLOV to 4 pin JST SH STEMMA QT / Qwiic Cable | 2 | $1.50 | [Product](https://www.adafruit.com/product/4483) |
| 4528 | Grove to STEMMA QT / Qwiic / JST SH Cable | 2 | $1.95 | [Product](https://www.adafruit.com/product/4528) |
| 5244 | Grove Cable Pigtail   2mm pitch 100mm long | 2 | $0.95 | [Product](https://www.adafruit.com/product/5244) |
| 5358 | DIY Magnetic Connector   Right Angle Four Contact Pins | 2 | $6.50 | [Product](https://www.adafruit.com/product/5358) |
| 5412 | Magnetic USB Charging Cable for 4 Pin 0.1" Magnetic Connector | 1 | $4.95 | [Product](https://www.adafruit.com/product/5412) |
| 5444 | RP SMA to w.FL / MHF3 / IPEX3 Adapter | 1 | $2.95 | [Product](https://www.adafruit.com/product/5444) |
| 954 | USB to TTL Serial Cable   Debug / Console Cable for Raspberry Pi | 1 | $9.95 | [Product](https://www.adafruit.com/product/954) · [Guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable) |

## Adafruit - Prototyping

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 1518 | Adafruit Flex Perma Proto   Half sized Breadboard Flex PCB | 1 | $7.50 | [Product](https://www.adafruit.com/product/1518) |
| 153 | Breadboarding wire bundle | 3 | $4.95 | [Product](https://www.adafruit.com/product/153) |
| 1609 | Adafruit Perma Proto Half sized Breadboard PCB   Single | 6 | $4.50 | [Product](https://www.adafruit.com/product/1609) · [Guide](https://learn.adafruit.com/adafruit-perma-proto-half-sized-breadboard-pcb) |
| 1883 | Silicone Cover Stranded Core Wire   2m 26AWG Orange | 1 | $0.95 | [Product](https://www.adafruit.com/product/1883) |
| 1950 | Premium Female/Female Jumper Wires   20 x 6" (150mm) | 1 | $1.95 | [Product](https://www.adafruit.com/product/1950) |
| 1953 | Premium Female/Male 'Extension' Jumper Wires   20 x 3" | 1 | $1.95 | [Product](https://www.adafruit.com/product/1953) |
| 2003 | Silicone Cover Stranded Core Wire   2m 30AWG Black | 1 | $0.75 | [Product](https://www.adafruit.com/product/2003) |
| 2005 | Silicone Cover Stranded Core Wire   2m 30AWG Green | 1 | $0.75 | [Product](https://www.adafruit.com/product/2005) |
| 239 | Full Sized Premium Breadboard   830 Tie Points | 8 | $5.95 | [Product](https://www.adafruit.com/product/239) |
| 3175 | Hook up Wire Spool Set   22AWG Stranded Core   10 x 25ft | 1 | $29.95 | [Product](https://www.adafruit.com/product/3175) |
| 3255 | Small Alligator Clip to Male Jumper Wire Bundle   12 Pieces | 1 | $7.95 | [Product](https://www.adafruit.com/product/3255) |
| 3417 | FeatherWing Tripler Mini Kit   Prototyping Add on For Feathers | 2 | $8.50 | [Product](https://www.adafruit.com/product/3417) · [Guide](https://learn.adafruit.com/featherwing-proto-and-doubler) |
| 4154 | Break away 0.1" 36 pin strip male header   Rainbow Combo 10 Pack | 2 | $4.95 | [Product](https://www.adafruit.com/product/4154) |
| 4160 | 20 pin 0.1" Female Headers   Rainbow Color Mix   5 pack | 2 | $2.50 | [Product](https://www.adafruit.com/product/4160) |
| 4354 | Adafruit Perma Proto 40 Pin Raspberry Pi Breadboard PCB Kit | 1 | $7.95 | [Product](https://www.adafruit.com/product/4354) · [Guide](https://learn.adafruit.com/adafruit-perma-proto-raspberry-pi-pcb) |
| 443 | Large Premium Solderless Breadboard | 2 | $19.95 | [Product](https://www.adafruit.com/product/443) |
| 64 | Half Sized Premium Breadboard   400 Tie Points | 1 | $5.00 | [Product](https://www.adafruit.com/product/64) |
| 758 | Premium Male/Male Jumper Wires   40 x 6" (150mm) | 4 | $3.95 | [Product](https://www.adafruit.com/product/758) |
| 759 | Premium Male/Male Jumper Wires   40 x 3" (75mm) | 1 | $3.95 | [Product](https://www.adafruit.com/product/759) |
| 760 | Premium Male/Male Jumper Wires   40 x 12" (300mm) | 1 | $7.95 | [Product](https://www.adafruit.com/product/760) |

## Adafruit - Power

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 380 | CR1220 12mm Diameter   3V Lithium Coin Cell Battery | 1 | $0.95 | [Product](https://www.adafruit.com/product/380) |
| 727 | 3 x AAA Battery Holder with On/Off Switch and 2 Pin JST | 1 | $1.95 | [Product](https://www.adafruit.com/product/727) |

## Adafruit - Kit

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 4263 | 4 H Circuit Playground Express   Base Kit | 1 | $29.95 | [Product](https://www.adafruit.com/product/4263) · [Guide](https://learn.adafruit.com/4-h-circuit-playground-express-base-kit) |
| 5128 | Adafruit MacroPad RP2040 Starter Kit   3x4 Keys   Encoder   OLED | 1 | $49.95 | [Product](https://www.adafruit.com/product/5128) · [Guide](https://learn.adafruit.com/adafruit-macropad-rp2040) |

## Adafruit - Tool

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 136 | Ladyada's Electronics Toolkit | 1 | $100.00 | [Product](https://www.adafruit.com/product/136) · [Guide](https://learn.adafruit.com/ladyadas-learn-arduino-lesson-number-0) |
| 151 | Panavise Jr. | 1 | $30.00 | [Product](https://www.adafruit.com/product/151) |
| 1528 | Oscilloscope Probe 100MHz | 1 | $14.95 | [Product](https://www.adafruit.com/product/1528) |
| 1592 | Short Wire Alligator Clip Test Lead (set of 12) | 1 | $3.95 | [Product](https://www.adafruit.com/product/1592) |
| 1597 | Engineer Professional Silicone Tip Solder Sucker | 1 | $17.50 | [Product](https://www.adafruit.com/product/1597) |
| 1598 | Professional IC Extraction Tool | 1 | $14.95 | [Product](https://www.adafruit.com/product/1598) |
| 2476 | Replacement Tubes for Professional Silicone Tip Solder Sucker | 1 | $1.95 | [Product](https://www.adafruit.com/product/2476) |
| 3019 | Third Hand Pana Hand Workstation Add On for Panavise | 1 | $39.95 | [Product](https://www.adafruit.com/product/3019) |
| 3217 | Maker Paste   Low Temperature Lead Free Prototyping Solder Paste | 1 | $6.95 | [Product](https://www.adafruit.com/product/3217) |
| 3540 | Square 60mm x 60mm Soldering Sponge – 3 Pack | 1 | $2.50 | [Product](https://www.adafruit.com/product/3540) |
| 3806 | Basic Lock sport Pick Set   9 Picks and 2 Wrenches | 1 | $6.95 | [Product](https://www.adafruit.com/product/3806) |
| 4559 | Pre Cut Multi Colored Heat Shrink Pack Kit   280 pcs | 1 | $9.95 | [Product](https://www.adafruit.com/product/4559) |

## Adafruit - Enclosure

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 3915 | Adafruit Circuit Playground Express or Bluefruit Enclosure | 3 | $4.95 | [Product](https://www.adafruit.com/product/3915) |
| 905 | Large Plastic Project Enclosure   Weatherproof with Clear Top | 1 | $19.95 | [Product](https://www.adafruit.com/product/905) |

## Adafruit - Storage

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 431 | Tiny Modular Snap Boxes   SMD component storage   10 pack | 1 | $3.95 | [Product](https://www.adafruit.com/product/431) |
| 432 | Small Modular Snap Boxes   SMD component storage   3 pack | 1 | $2.95 | [Product](https://www.adafruit.com/product/432) |
| 433 | Medium Modular Snap Boxes   SMD component storage   2 pack | 1 | $2.95 | [Product](https://www.adafruit.com/product/433) |
| 434 | Large Modular Snap Box   SMD component storage | 3 | $1.95 | [Product](https://www.adafruit.com/product/434) |

## Adafruit - Accessory

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 2046 | Potentiometer Knob   Soft Touch T18   Red | 1 | $0.50 | [Product](https://www.adafruit.com/product/2046) |
| 2047 | Potentiometer Knob   Soft Touch T18   White | 1 | $0.50 | [Product](https://www.adafruit.com/product/2047) |
| 2055 | Scrubber Knob for Rotary Encoder   35mm | 1 | $0.95 | [Product](https://www.adafruit.com/product/2055) |
| 2056 | Solid Machined Metal Knob   1" Diameter | 1 | $3.95 | [Product](https://www.adafruit.com/product/2056) |
| 2830 | Stacking Headers for Feather   12 pin and 16 pin female headers | 5 | $1.25 | [Product](https://www.adafruit.com/product/2830) |
| 2940 | Short Headers Kit for Feather   12 pin   16 pin Female Headers | 8 | $1.50 | [Product](https://www.adafruit.com/product/2940) |
| 3002 | Short Feather Male Headers   12 pin and 16 pin Male Header Set | 4 | $0.50 | [Product](https://www.adafruit.com/product/3002) |
| 3299 | Black Nylon Machine Screw and Stand off Set – M2.5 Thread | 1 | $16.95 | [Product](https://www.adafruit.com/product/3299) |
| 3340 | 900Mhz Antenna Kit   For LoPy, LoRa, etc | 1 | $12.75 | [Product](https://www.adafruit.com/product/3340) |
| 3585 | Great Scott Gadgets ANT700   300MHz to 1100MHz Telescope Antenna | 1 | $27.95 | [Product](https://www.adafruit.com/product/3585) |
| 3804 | Large Clear Practice Padlock | 1 | $7.50 | [Product](https://www.adafruit.com/product/3804) |
| 4036 | DIY Ornament Kit   6cm Diameter   Perfect for Circuit Playground | 1 | $1.95 | [Product](https://www.adafruit.com/product/4036) |
| 4103 | Bolt On Kit for Circuit Playground, micro:bit, Flora or Gemma | 1 | $1.50 | [Product](https://www.adafruit.com/product/4103) |
| 4269 | Simple Spring Antenna   915MHz | 1 | $0.95 | [Product](https://www.adafruit.com/product/4269) |
| 4594 | Black LED Diffusion Acrylic Panel 12" x 12"   0.1" / 2.6mm thick | 1 | $9.95 | [Product](https://www.adafruit.com/product/4594) |
| 4631 | Mini Magnet Feet for RGB LED Matrices (Pack of 4) | 1 | $2.50 | [Product](https://www.adafruit.com/product/4631) |
| 4813 | Clear Adhesive Squares   6 pack | 1 | $0.50 | [Product](https://www.adafruit.com/product/4813) |
| 5051 | Black Anodized Aluminum Bumper Feet   Pack of 2 | 1 | $8.95 | [Product](https://www.adafruit.com/product/5051) |
| 5093 | Slim Rubber Rotary Encoder Knob   11.5mm x 14.5mm D Shaft | 2 | $0.75 | [Product](https://www.adafruit.com/product/5093) |
| 5195 | Etched Glow Through Keycap with LGTM (Looks Good To Me) Acronym | 1 | $4.95 | [Product](https://www.adafruit.com/product/5195) |
| 5527 | Anodized Aluminum Machined Knob   Black   20mm Diameter | 1 | $2.95 | [Product](https://www.adafruit.com/product/5527) |
| 5531 | Anodized Aluminum Machined Knob   Gold   20mm Diameter | 1 | $2.95 | [Product](https://www.adafruit.com/product/5531) |
| 669 | ESD (Electrostatic discharge)   Sticker! | 2 | $1.50 | [Product](https://www.adafruit.com/product/669) |

## Adafruit - Book/Subscription

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 3067 | AdaBox Subscription | 1 | — | [Product](https://www.adafruit.com/product/3067) · [Guide](https://learn.adafruit.com/adabox) |
| 4220 | Learn CircuitPython with 1 Month Subscription to Codecademy Pro | 1 | $19.99 | [Product](https://www.adafruit.com/product/4220) · [Guide](https://learn.adafruit.com/welcome-to-circuitpython) |
| 5154 | Digi Key Innovation Handbook | 1 | $5.95 | [Product](https://www.adafruit.com/product/5154) |

---

# Pimoroni Products

## Pimoroni - Microcontroller

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| PIM560 | Pimoroni Pico LiPo - 16MB | 1 | £11.25 | [Product](https://shop.pimoroni.com/products/pimoroni-pico-lipo) · [Guide](https://learn.pimoroni.com/article/getting-started-with-pico-lipo) |

## Pimoroni - Sensor

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| ADA4258 | Adafruit LPS35HW Water Resistant Pressure Sensor - STEMMA QT | 1 | £4.80 | [Product](https://www.adafruit.com/product/4258) · [Guide](https://learn.adafruit.com/adafruit-lps35hw-water-resistant-barometric-pressure-sensor) |
| BOB-19389 | SparkFun Analog MEMS Microphone Breakout - SPH8878LR5H-1 | 1 | £4.55 | [Product](https://www.sparkfun.com/products/19389) · [Guide](https://learn.sparkfun.com/tutorials/analog-mems-microphone-breakout---sph8878lr5h-1-hookup-guide) |
| PIM373 | VL53L1X Time of Flight (ToF) Sensor Breakout | 1 | £8.90 | [Product](https://shop.pimoroni.com/products/vl53l1x-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-vl53l1x-breakout) |
| PIM438 | MAX30101 Breakout - Heart Rate, Oximeter, Smoke Sensor | 1 | £8.90 | [Product](https://shop.pimoroni.com/products/max30101-breakout-heart-rate-oximeter-smoke-sensor) · [Guide](https://learn.pimoroni.com/article/getting-started-with-max30101-breakout) |
| PIM569 | MICS6814 3-in-1 Gas Sensor Breakout (CO, NO2, NH3) | 1 | £19.25 | [Product](https://shop.pimoroni.com/products/mics6814-gas-sensor-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-mics6814-breakout) |
| PIM575 | BME688 4-in-1 Air Quality Breakout (Gas, Temperature, Pressure, Humidity) | 1 | £12.05 | [Product](https://shop.pimoroni.com/products/bme688-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-bme688-breakout) |
| PIM587 | SCD41 CO2 Sensor Breakout (Carbon Dioxide / Temperature / Humidity) | 1 | £45.50 | [Product](https://shop.pimoroni.com/products/scd41-co2-sensor-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-scd41-co2-breakout) |

## Pimoroni - Display

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| ADA715 | Adafruit I2C Controlled + Keypad Shield Kit for 16x2 LCD | 1 | £3.10 | [Product](https://www.adafruit.com/product/715) · [Guide](https://learn.adafruit.com/adafruit-i2c-controlled-keypad-shield-for-16x2-lcd) |
| PIM333 | Scroll pHAT HD - Yellow | 1 | £3.45 | [Product](https://shop.pimoroni.com/products/scroll-phat-hd) · [Guide](https://learn.pimoroni.com/article/getting-started-with-scroll-phat-hd) |
| PIM435 | 5x5 RGB Matrix Breakout | 1 | £4.10 | [Product](https://shop.pimoroni.com/products/5x5-rgb-matrix-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-5x5-rgb-matrix-breakout) |
| PIM442 | 11x7 LED Matrix Breakout | 1 | £6.25 | [Product](https://shop.pimoroni.com/products/11x7-led-matrix-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-11x7-led-matrix-breakout) |
| PIM527 | LED Dot Matrix Breakout - Green | 1 | £3.55 | [Product](https://shop.pimoroni.com/products/led-dot-matrix-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-led-dot-matrix-breakout) |

## Pimoroni - Breakout Board

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| ADA5664 | Adafruit PCA9546 4-Channel STEMMA QT / Qwiic I2C Multiplexer | 1 | £3.50 | [Product](https://www.adafruit.com/product/5664) · [Guide](https://learn.adafruit.com/adafruit-pca9546-4-channel-i2c-multiplexer) |
| PIM301 | Button SHIM | 1 | £4.50 | [Product](https://shop.pimoroni.com/products/button-shim) · [Guide](https://learn.pimoroni.com/article/getting-started-with-button-shim) |
| PIM447 | Trackball Breakout | 1 | £12.75 | [Product](https://shop.pimoroni.com/products/trackball-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-trackball-breakout) |
| PIM449 | RV3028 Real-Time Clock (RTC) Breakout | 1 | £7.50 | [Product](https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-rv3028-real-time-clock-breakout) |
| PIM455 | HT0740 40V / 10A Switch Breakout | 1 | £11.75 | [Product](https://shop.pimoroni.com/products/ht0740-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-ht0740-breakout) |
| PIM479 | DRV8830 DC Motor Driver Breakout | 1 | £5.40 | [Product](https://shop.pimoroni.com/products/drv8830-dc-motor-driver-breakout) · [Guide](https://learn.pimoroni.com/article/getting-started-with-drv8830-motor-driver-breakout) |
| PIM517 | IO Expander Breakout | 1 | £4.20 | [Product](https://shop.pimoroni.com/products/io-expander) · [Guide](https://learn.pimoroni.com/article/getting-started-with-io-expander-breakout) |
| POL-5065 | Motoron Dual Motor Controller - M2T256 - I2C | 1 | £6.90 | [Product](https://www.pololu.com/product/5065) |

## Pimoroni - FeatherWing

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| ADA3135 | Adafruit 15x7 CharliePlex LED Matrix Display FeatherWing - Yellow | 1 | £2.25 | [Product](https://www.adafruit.com/product/3135) · [Guide](https://learn.adafruit.com/adafruit-15x7-7x15-charlieplex-led-matrix-display-featherwing) |

## Pimoroni - Component

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| COM0216 | Optoisolator - 1 Channel | 1 | £0.55 | [Product](https://shop.pimoroni.com/products/optoisolator-1-channel) |
| WPM463 | 2 Channel Solid State Relay Module | 1 | £3.30 | [Product](https://shop.pimoroni.com/products/2-channel-solid-state-relay-module) |

## Pimoroni - Cable/Connector

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| COM3900 | Breakout Garden I2C Connector (pack of 5) | 1 | £2.35 | [Product](https://shop.pimoroni.com/products/breakout-garden-i2c-connector-pack-of-5) |
| PIM409 | I2C Breakout Extender (pack of 3) | 1 | £1.90 | [Product](https://shop.pimoroni.com/products/breakout-extender) |
| PIM572 | Breakout Garden to STEMMA QT / Qwiic Adapter | 4 | £0.80 | [Product](https://shop.pimoroni.com/products/breakout-garden-to-qwiic-adaptor) |

## Pimoroni - Prototyping

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| ADA1207 | Adafruit SMT breakout PCB for SOIC or TSSOP - 16 pin - pack of three | 1 | £2.75 | [Product](https://www.adafruit.com/product/1207) |
| ADA1211 | Adafruit SMT breakout PCB for SOIC or TSSOP - 12 pin - pack of six | 1 | £3.40 | [Product](https://www.adafruit.com/product/1211) |

## Pimoroni - Power

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| POL-2122 | Pololu 3.3V Step-Up/Step-Down Voltage Regulator S7V8F3 | 1 | £4.60 | [Product](https://www.pololu.com/product/2122) |
| POL-3781 | Step-Down Voltage Regulator D36V28Fx - 3.3V 3.6A | 1 | £6.55 | [Product](https://www.pololu.com/product/3781) |

## Pimoroni - Tool

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| IFIX-EU145439-1 | Mahi 1/4" Bit Driver | 1 | £4.60 | [Product](https://www.ifixit.com/products/mahi-driver) |
| PA-21 | Engineer Universal Crimping Pliers | 1 | £26.00 | [Product](https://shop.pimoroni.com/products/universal-crimping-pliers) |

## Pimoroni - Accessory

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| COM0005 | Pico Stacking Header Pack | 3 | £0.75 | [Product](https://shop.pimoroni.com/products/pico-stacking-headers) |
| COM1117 | Pico Header Pack | 3 | £0.90 | [Product](https://shop.pimoroni.com/products/pico-header-pack) |
| PIM321 | pHAT Stack - Solder Yourself Kit | 1 | £2.95 | [Product](https://shop.pimoroni.com/products/phat-stack) · [Guide](https://learn.pimoroni.com/article/assembling-phat-stack) |
| PIM461 | Fan SHIM for Raspberry Pi | 1 | £10.00 | [Product](https://shop.pimoroni.com/products/fan-shim) · [Guide](https://learn.pimoroni.com/article/getting-started-with-fan-shim) |
| PIM549 | Pico Breakout Garden Base | 1 | £11.00 | [Product](https://shop.pimoroni.com/products/pico-breakout-garden-base) · [Guide](https://learn.pimoroni.com/article/getting-started-with-pico-breakout-garden) |
| PIM699 | NVMe Base for Raspberry Pi 5 | 1 | £11.25 | [Product](https://shop.pimoroni.com/products/nvme-base) · [Guide](https://learn.pimoroni.com/article/getting-started-with-nvme-base) |

---

# Waveshare Products

## Waveshare - Display

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 10.4HP-CAPQLED | Waveshare 10.4HP-CAPQLED | 1 | — | [Product](https://www.waveshare.com/10.4hp-capqled.htm) · [Guide](https://www.waveshare.com/wiki/10.4HP-CAPQLED) |

---

# SparkFun Products

## SparkFun - Breakout Board

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| ROB-16836 | SparkFun ProDriver TC78H670FTG | 1 | — | [Product](https://www.sparkfun.com/sparkfun-prodriver-stepper-motor-driver-tc78h670ftg.html) · [Guide](https://learn.sparkfun.com/tutorials/sparkfun-prodriver-and-mini-stepper-motor-driver-hookup-guide/all) |

---

# Mouser Products

## Mouser - Sensor

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| TF03-100 | Benewake TF03-100 LiDAR | 1 | — | [Product](https://en.benewake.com/TF03/index_proid_329.html) · [Guide](https://www.mouser.com/catalog/specsheets/Benewake_10152020_TF03-100.pdf) |

---

# AliExpress Products

## AliExpress - Microcontroller

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| AE-3256802908925724 | LilyGO T-Display-S3 (AliExpress) | 1 | — | [Product](https://www.aliexpress.us/item/3256802908925724.html) · [Guide](https://github.com/Xinyuan-LilyGO/T-Display-S3) |
| T-Display-S3 | LilyGO T-Display-S3 | 1 | — | [Product](https://lilygo.cc/products/t-display-s3) · [Guide](https://github.com/Xinyuan-LilyGO/T-Display-S3) |
| Wrist-E-Paper | LilyGO Wrist-E-Paper | 1 | — | [Product](https://github.com/Xinyuan-LilyGO/Wrist-E-Paper) · [Guide](https://github.com/Xinyuan-LilyGO/Wrist-E-Paper) |
| esp32-dev-board-wi-fi-bluetooth-ch9102x | ESP32 Dev Board, Wi-Fi + Bluetooth (CH9102X) | 1 | $3.65 |  |
| mega-2560-pro-embed-board-atmega2560-ch340g | Mega 2560 PRO Embed Board (ATmega2560 + CH340G) | 1 | $8.95 |  |
| nodemcu-v2-1-esp8266-esp-12e-wi-fi-board-ch9102 | NodeMCU V2.1 ESP8266 ESP-12E Wi-Fi Board (CH9102) | 1 | $2.43 |  |
| nodemcu-v3-esp8266-wi-fi-development-board-ch340 | NodeMCU V3 ESP8266 Wi-Fi Development Board (CH340) | 1 | $2.07 |  |
| stm32f411ceu6-core-development-board | STM32F411CEU6 Core Development Board | 1 | $5.89 |  |

## AliExpress - Sensor

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 12v-rain-sensor-relay-control-module | 12V Rain Sensor Relay Control Module | 1 | $1.62 |  |
| aht10-temperature-and-humidity-sensor-module-i2c | AHT10 Temperature and Humidity Sensor Module (I2C) | 1 | $1.19 |  |
| d203s-pyroelectric-pir-sensor-10-pcs | D203S Pyroelectric PIR Sensor (10 pcs) | 1 | $3.35 |  |
| dht22-am2302-temperature-and-humidity-sensor-module | DHT22 (AM2302) Temperature and Humidity Sensor Module | 1 | $3.41 |  |
| e3jk-5dm1-photoelectric-beam-sensor-switch-5-m-12-24v-dc | E3JK-5DM1 Photoelectric Beam Sensor Switch (5 m, 12-24V DC) | 1 | $4.24 |  |
| generic-scd41-co2-sensor-module-purple | Generic SCD41 CO2 Sensor Module (purple) | 1 | — |  |
| gy-271-hmc5883l-3-axis-compass-module | GY-271 HMC5883L 3-Axis Compass Module | 1 | $1.86 |  |
| gy-273-hmc5883l-3-axis-magnetometer-compass-module | GY-273 HMC5883L 3-Axis Magnetometer (Compass) Module | 1 | $1.62 |  |
| gy-31-tcs3200-color-sensor-module | GY-31 TCS3200 Color Sensor Module | 1 | $2.51 |  |
| inmp441-i2s-mems-omnidirectional-microphone-module | INMP441 I2S MEMS Omnidirectional Microphone Module | 1 | $1.74 |  |
| ir-obstacle-avoidance-sensor-module | IR Obstacle Avoidance Sensor Module | 1 | $0.35 |  |
| jsn-sr04t-aj-sr04m-waterproof-ultrasonic-distance-sensor | JSN-SR04T / AJ-SR04M Waterproof Ultrasonic Distance Sensor | 1 | $5.51 |  |
| rpr220-reflective-optical-sensor-10-pcs | RPR220 Reflective Optical Sensor (10 pcs) | 1 | $1.68 |  |
| slot-type-optocoupler-speed-sensor-module-lm393 | Slot-Type Optocoupler Speed Sensor Module (LM393) | 1 | $0.41 |  |
| sound-detection-sensor-module-microphone-digital-out | Sound Detection Sensor Module (Microphone, Digital Out) | 1 | $0.48 |  |
| sr602-mini-pir-motion-sensor-module-with-lens | SR602 Mini PIR Motion Sensor Module (with Lens) | 1 | $0.94 |  |
| sw-520d-ball-tilt-switch-10-pcs | SW-520D Ball Tilt Switch (10 pcs) | 1 | $0.80 |  |
| sw-520d-tilt-sensor-module-lm393 | SW-520D Tilt Sensor Module (LM393) | 1 | $0.56 |  |
| vibration-shock-sensor-module-sw-18010p-lm393 | Vibration / Shock Sensor Module (SW-18010P, LM393) | 1 | $0.40 |  |
| vs1838b-38khz-ir-receiver-10-pcs | VS1838B 38kHz IR Receiver (10 pcs) | 1 | $0.99 |  |
| xxw-5818-vibration-shock-switch-20-pcs | XXW-5818 Vibration / Shock Switch (20 pcs) | 1 | $1.39 |  |

## AliExpress - Display

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 0-91-128x32-oled-display-module-ssd1306-i2c-white | 0.91" 128x32 OLED Display Module (SSD1306, I2C, White) | 1 | $1.52 |  |
| 10-segment-4-colour-led-bar-graph-display-10-pcs | 10-Segment 4-Colour LED Bar Graph Display (10 pcs) | 1 | $3.05 |  |
| 8x8-red-led-dot-matrix-32mm-common-cathode-1088ab | 8x8 Red LED Dot Matrix, 32mm Common Cathode (1088AB) | 1 | $1.20 |  |
| max7219-4-in-1-8x8-led-dot-matrix-display-module-blue | MAX7219 4-in-1 8x8 LED Dot Matrix Display Module (Blue) | 1 | $3.66 |  |
| p3-rgb-led-matrix-panel-64x32-192x96mm-smd2121 | P3 RGB LED Matrix Panel, 64x32, 192x96mm (SMD2121) | 1 | $13.39 |  |
| tm1637-4-digit-7-segment-led-display-module-0-56in-white | TM1637 4-Digit 7-Segment LED Display Module, 0.56in (White) | 1 | $1.04 |  |

## AliExpress - LED

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 10mm-water-clear-led-assortment-5-colours | 10mm Water-Clear LED Assortment (5 colours) | 1 | $0.64 |  |
| 12-led-piranha-white-led-board-3-5v | 12-LED Piranha White LED Board (3-5V) | 1 | $0.81 |  |
| 3mm-led-assortment-100-pcs-5-colours | 3mm LED Assortment (100 pcs, 5 colours) | 1 | $0.90 |  |
| 3w-high-power-led-on-20mm-star-warm-white | 3W High-Power LED on 20mm Star (Warm White) | 1 | $1.27 |  |
| 5mm-940nm-ir-led-and-ir-receiver-diode-pairs-10-pairs | 5mm 940nm IR LED and IR Receiver Diode Pairs (10 pairs) | 3 | $1.70 |  |
| 5mm-prewired-12v-diffused-led-kit-with-8mm-holders-10-pcs | 5mm Prewired 12V Diffused LED Kit with 8mm Holders (10 pcs) | 1 | $4.98 |  |
| 8mm-straw-hat-white-led-0-5w-10-pcs | 8mm Straw Hat White LED, 0.5W (10 pcs) | 1 | $0.52 |  |
| mini-bluetooth-rgb-led-strip-music-controller-5-24v | Mini Bluetooth RGB LED Strip Music Controller (5-24V) | 1 | $1.28 |  |
| pir-motion-sensor-led-night-light-85-265v | PIR Motion Sensor LED Night Light (85-265V) | 1 | $2.90 |  |

## AliExpress - Breakout Board

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 01studio-pihat-expansion-board-for-raspberry-pi-with-oled | 01Studio PiHAT Expansion Board for Raspberry Pi (with OLED) | 1 | $18.51 |  |
| keyestudio-pcf8591-a-d-converter-module-for-raspberry-pi | Keyestudio PCF8591 A/D Converter Module for Raspberry Pi | 1 | $4.99 |  |

## AliExpress - Motor/Actuator

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 716-coreless-vibration-motor-waterproof-1-5-3-7v-3-7-5v | 716 Coreless Vibration Motor, Waterproof (1.5-3.7V / 3.7-5V) | 1 | $1.54 |  |
| 8mm-coin-vibration-motor-3v-2-pcs | 8mm Coin Vibration Motor 3V (2 pcs) | 1 | $0.39 |  |
| a2212-1000kv-brushless-outrunner-motor | A2212 1000KV Brushless Outrunner Motor | 1 | $4.94 |  |
| ds3218-20kg-waterproof-digital-servo-270-degree | DS3218 20kg Waterproof Digital Servo (270 Degree) | 1 | $10.10 |  |
| dual-channel-12v-peristaltic-dosing-pump | Dual-Channel 12V Peristaltic Dosing Pump | 1 | $9.50 |  |
| gim8108-quadruped-robot-joint-actuator-mit-mini-cheetah-styl | GIM8108 Quadruped Robot Joint Actuator (MIT Mini Cheetah style, 6:1) | 1 | $328.90 |  |
| injora-550-brushed-motor-21t | INJORA 550 Brushed Motor 21T | 1 | $9.99 |  |
| injora-injs025-35kg-digital-servo-270 | INJORA INJS025 35kg Digital Servo (270°) | 1 | $15.99 |  |
| jgy370-worm-gear-motor-6v-150-rpm | JGY370 Worm Gear Motor (6V, 150 RPM) | 1 | $8.48 |  |
| mg996r-metal-gear-digital-servo-13-15-kg-4-pcs | MG996R Metal Gear Digital Servo (13-15 kg, 4 pcs) | 1 | $17.64 |  |
| nidec-25mm-geared-stepper-motor-2-phase-1-12 | Nidec 25mm Geared Stepper Motor (2-Phase, 1:12) | 1 | $1.37 |  |
| open-smart-5v-electromagnet-module-10n-holding | OPEN-SMART 5V Electromagnet Module (10N Holding) | 1 | $4.20 |  |
| sg90-mg90s-9g-micro-servo | SG90 / MG90S 9g Micro Servo | 1 | $1.69 |  |
| stepperonline-nema-17-short-body-stepper-17hs08-1004s-16ncm | STEPPERONLINE Nema 17 Short-Body Stepper 17HS08-1004S (16Ncm) | 1 | $7.99 |  |
| vibration-motor-module-5v | Vibration Motor Module (5V) | 1 | $0.52 |  |
| vibration-motor-module-5v-2 | Vibration Motor Module (5V) (2) | 1 | $0.51 |  |

## AliExpress - Motor Driver/ESC

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 20a-brushed-esc-with-brake-2s | 20A Brushed ESC with Brake (2S) | 1 | $3.28 |  |
| 3-channel-servo-esc-tester-ccpm | 3-Channel Servo / ESC Tester (CCPM) | 1 | $1.75 |  |
| digital-display-pwm-dc-motor-speed-controller-40a | Digital Display PWM DC Motor Speed Controller (40A) | 1 | $5.26 |  |
| drv8833-dual-channel-dc-motor-driver-module-1-5a | DRV8833 Dual-Channel DC Motor Driver Module (1.5A) | 1 | $0.67 |  |
| hobbywing-quicrun-1060-60a-brushed-esc-1-10-rc | HobbyWing QuicRun 1060 60A Brushed ESC (1/10 RC) | 1 | $21.31 |  |
| keyestudio-pca9685-16-channel-servo-driver-shield | Keyestudio PCA9685 16-Channel Servo Driver Shield | 1 | $7.19 |  |
| mini-20a-brushed-esc-forward-reverse-with-brake-2s | Mini 20A Brushed ESC, Forward/Reverse with Brake (2S) | 1 | $3.03 |  |
| pwm-dc-motor-speed-controller-10-60v-20a | PWM DC Motor Speed Controller (10-60V, 20A) | 1 | $3.26 |  |
| pwm-dc-motor-speed-controller-with-display-10-55v-40a | PWM DC Motor Speed Controller with Display (10-55V, 40A) | 1 | $11.35 |  |
| red-brick-50a-brushless-esc-2-3s-5v-bec | Red Brick 50A Brushless ESC (2-3S, 5V BEC) | 1 | $13.38 |  |

## AliExpress - Switch/Button

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 16mm-metal-latching-push-button-with-blue-ring-led-6v | 16mm Metal Latching Push Button with Blue Ring LED (6V) | 1 | $1.27 |  |
| 16mm-rgb-led-latching-toggle-switch-spst-ip67-12-24v | 16mm RGB LED Latching Toggle Switch, SPST, IP67 (12-24V) | 1 | $4.99 |  |
| bathroom-mirror-touch-switch-for-led-lights-5-12v | Bathroom Mirror Touch Switch for LED Lights (5-12V) | 1 | $3.35 |  |
| capacitive-touch-switch-module-httm-rgb-flash | Capacitive Touch Switch Module (HTTM, RGB Flash) | 1 | $0.66 |  |
| daiertek-16mm-ip67-rgb-led-toggle-switch-spst-12v | Daiertek 16mm IP67 RGB LED Toggle Switch (SPST, 12V) | 1 | $4.99 |  |
| ec11-rotary-encoder-360-degree-5-pcs | EC11 Rotary Encoder, 360 Degree (5 pcs) | 1 | $2.33 |  |
| lanboo-16mm-metal-toggle-button-switch-with-led-ring-latchin | LANBOO 16mm Metal Toggle Button Switch with LED Ring, Latching | 1 | $0.60 |  |
| lanboo-22mm-15a-metal-push-button-switch-ip67 | LANBOO 22mm 15A Metal Push Button Switch, IP67 | 1 | $0.60 |  |
| mts-102-103-202-203-mini-toggle-switches-6mm-5-10-pcs | MTS-102/103/202/203 Mini Toggle Switches, 6mm (5/10 pcs) | 1 | $2.11 |  |

## AliExpress - Audio

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 12v-85db-mini-electronic-alarm-buzzer | 12V 85dB Mini Electronic Alarm Buzzer | 1 | $0.75 |  |
| 5v-active-buzzer-12x9-5mm-10-pcs | 5V Active Buzzer, 12x9.5mm (10 pcs) | 1 | $1.35 |  |
| aiyima-44mm-8-ohm-20w-full-range-vibration-speaker | AIYIMA 44mm 8 Ohm 20W Full-Range Vibration Speaker | 1 | $13.32 |  |
| mini-pcb-mount-speaker-8-0-5w | Mini PCB-Mount Speaker 8Ω 0.5W | 1 | $1.40 |  |
| qolelarm-120db-wired-mini-siren-6-12v-dc | Qolelarm 120dB Wired Mini Siren (6-12V DC) | 1 | $2.75 |  |

## AliExpress - Wireless/RF

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 315mhz-rf-transmitter-and-receiver-module-pair | 315MHz RF Transmitter and Receiver Module Pair | 1 | $0.75 |  |
| 433mhz-1-channel-12v-relay-receiver-with-rf-remote | 433MHz 1-Channel 12V Relay Receiver with RF Remote | 1 | $3.40 |  |
| 433mhz-4-button-cloning-remote-control | 433MHz 4-Button Cloning Remote Control | 1 | $1.79 |  |
| cdm324-24ghz-microwave-radar-motion-sensor-module | CDM324 24GHz Microwave Radar Motion Sensor Module | 1 | $3.60 |  |
| lilygo-t-micro32-plus-esp32-module-8mb-flash-2mb-psram | LILYGO T-Micro32 Plus ESP32 Module (8MB Flash, 2MB PSRAM) | 1 | $6.98 |  |
| sim800l-quad-band-gsm-gprs-module-micro-sim | SIM800L Quad-Band GSM/GPRS Module (Micro SIM) | 1 | $1.82 |  |

## AliExpress - Component

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 2-channel-12v-relay-module-with-optocoupler | 2-Channel 12V Relay Module with Optocoupler | 1 | $1.38 |  |
| aluminium-electrolytic-capacitor-kit-120-pcs-0-22-470-f | Aluminium Electrolytic Capacitor Kit (120 pcs, 0.22-470 µF) | 1 | $1.44 |  |
| aluminum-electrolytic-capacitor-kit-0-1-1000uf-24-values-500 | Aluminum Electrolytic Capacitor Kit, 0.1-1000uF, 24 values (500 pcs) | 2 | $15.80 |  |
| gl5528-photoresistor-ldr-20-pcs | GL5528 Photoresistor LDR (20 pcs) | 1 | $0.48 |  |
| hk19f-12v-sealed-pcb-relay-5-pcs | HK19F 12V Sealed PCB Relay (5 pcs) | 1 | $2.69 |  |
| jccon-low-esr-electrolytic-capacitor-kit-1-470uf-15-values-2 | JCCON Low-ESR Electrolytic Capacitor Kit, 1-470uF, 15 values (225 pcs) | 1 | $8.18 |  |
| polyester-film-capacitor-kit-24-values-100v-660-pcs | Polyester Film Capacitor Kit, 24 values, 100V (660 pcs) | 1 | $18.84 |  |
| rm065-trimmer-potentiometer-kit-500-ohm-1m-100-pcs | RM065 Trimmer Potentiometer Kit, 500 Ohm-1M (100 pcs) | 1 | $5.94 |  |
| srd-12vdc-sl-c-12v-pcb-power-relay-5-pcs | SRD-12VDC-SL-C 12V PCB Power Relay (5 pcs) | 1 | $1.72 |  |
| tec1-12712-peltier-thermoelectric-cooler-40x40mm-12a | TEC1-12712 Peltier Thermoelectric Cooler (40x40mm, 12A) | 1 | $3.17 |  |

## AliExpress - Cable/Connector

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| fpc-ffc-adapter-board-0-5mm-pitch-30-pin | FPC/FFC Adapter Board, 0.5mm pitch, 30-pin | 3 | $0.73 |  |
| fpc-ffc-adapter-board-1-0mm-pitch-30-pin | FPC/FFC Adapter Board, 1.0mm pitch, 30-pin | 3 | $0.77 |  |
| kf141r-2-pin-2-54mm-spring-terminal-block-5-pcs | KF141R 2-Pin 2.54mm Spring Terminal Block (5 pcs) | 1 | $0.75 |  |
| kf301-3p-5-08mm-3-pin-screw-terminal-block-10-pcs | KF301-3P 5.08mm 3-Pin Screw Terminal Block (10 pcs) | 1 | $0.64 |  |
| silicone-hookup-wire-kit-22awg-box-1-5-colours-30-m | Silicone Hookup Wire Kit 22AWG (Box 1, 5 colours, 30 m) | 1 | $13.90 |  |

## AliExpress - Power

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 12v-battery-undervoltage-cut-off-relay-module-yx-x0001 | 12V Battery Undervoltage Cut-off Relay Module (YX-X0001) | 1 | $1.97 |  |
| 15kv-high-voltage-arc-ignition-generator-kit-3-7v | 15kV High-Voltage Arc Ignition Generator Kit (3.7V) | 1 | $1.46 |  |
| 3s-18650-power-wall-battery-holder-board-3s2p-no-bms | 3S 18650 Power Wall Battery Holder Board, 3S2P (no BMS) | 1 | $11.25 |  |
| 3s-40a-li-ion-bms-protection-board-enhanced-18650 | 3S 40A Li-ion BMS Protection Board, Enhanced (18650) | 1 | $0.99 |  |
| 400kv-high-voltage-pulse-generator-module-3-7-6v | 400kV High-Voltage Pulse Generator Module (3.7-6V) | 1 | $1.79 |  |
| 4s-40a-li-ion-bms-protection-board-balanced-18650 | 4S 40A Li-ion BMS Protection Board, Balanced (18650) | 3 | $1.47 |  |
| ams1117-3-3-ldo-voltage-regulator-ic-20-pcs | AMS1117-3.3 LDO Voltage Regulator IC (20 pcs) | 1 | $1.42 |  |
| ams1117-5-0-ldo-voltage-regulator-ic-20-pcs | AMS1117-5.0 LDO Voltage Regulator IC (20 pcs) | 1 | $1.42 |  |
| diymore-18650-battery-shield-v3-usb-power-board | diymore 18650 Battery Shield V3 (USB Power Board) | 1 | $1.72 |  |
| dual-18650-battery-shield-v8-5v-3a-3v-1a | Dual 18650 Battery Shield V8 (5V/3A, 3V/1A) | 1 | $7.18 |  |
| isdt-pd60-60w-lipo-balance-charger-usb-c-input | ISDT PD60 60W LiPo Balance Charger (USB-C Input) | 1 | $23.56 |  |
| lm2596-adjustable-step-down-converter-module | LM2596 Adjustable Step-Down Converter Module | 1 | $2.39 |  |
| sx1308-adjustable-boost-converter-2-24v-to-2-28v-2a | SX1308 Adjustable Boost Converter (2-24V to 2-28V, 2A) | 1 | $0.40 |  |
| usb-c-18650-li-ion-charger-board-with-protection-5v-1a-10-pc | USB-C 18650 Li-ion Charger Board with Protection, 5V 1A (10 pcs) | 1 | $6.87 |  |
| usb-fast-charge-step-down-module-qc3-0-pd-8-32v-in-20w | USB Fast-Charge Step-Down Module, QC3.0/PD (8-32V in, 20W) | 1 | $4.08 |  |

## AliExpress - Battery

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| hrb-2s-7-4v-5200mah-50c-lipo-battery-t-plug-hard-case | HRB 2S 7.4V 5200mAh 50C LiPo Battery (T Plug, Hard Case) | 1 | $27.96 |  |
| hrb-3s-11-1v-2600mah-35c-lipo-battery-xt60 | HRB 3S 11.1V 2600mAh 35C LiPo Battery (XT60) | 1 | $21.12 |  |
| liitokala-lii-31s-18650-li-ion-cell-3100mah-35a | LiitoKala Lii-31S 18650 Li-ion Cell (3100mAh, 35A) | 1 | $7.25 |  |
| ncr18650b-3400mah-18650-li-ion-cell-2-pcs | NCR18650B 3400mAh 18650 Li-ion Cell (2 pcs) | 1 | $7.80 |  |

## AliExpress - Kit

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| a2212-1000kv-brushless-motor-30a-esc-and-sg90-servo-set | A2212 1000KV Brushless Motor, 30A ESC and SG90 Servo Set | 1 | $13.29 |  |
| single-axis-solar-tracker-module-light-seeking | Single-Axis Solar Tracker Module (Light-Seeking) | 1 | $2.90 |  |

## AliExpress - Tool

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| fnirsi-multi-purpose-transistor-lcr-tester-tft | FNIRSI Multi-Purpose Transistor / LCR Tester (TFT) | 1 | $15.10 |  |
| portable-12v-spot-welder-pcb-for-18650-nickel-strip-v7 | Portable 12V Spot Welder PCB for 18650 Nickel Strip (V7) | 1 | $8.50 |  |
| portable-led-tester-box-2-150-ma | Portable LED Tester Box (2-150 mA) | 1 | $3.28 |  |
| smd-test-clip-tweezer-probe-for-lcr-testers | SMD Test Clip / Tweezer Probe for LCR Testers | 1 | $1.87 |  |

---

# Amazon Products

## Amazon - Microcontroller

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| arduino-uno-rev3-a000066 | Arduino UNO Rev3 (A000066) | 1 | $26.95 |  |

---

# Orbtronic Products

## Orbtronic - Battery

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| samsung-35e-18650-li-ion-cell-3500mah-flat-top-inr18650-35e | Samsung 35E 18650 Li-ion Cell, 3500mAh, Flat Top (INR18650-35E) | 1 | $9.99 |  |

---

# Battery Junction Products

## Battery Junction - Battery

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| samsung-35e-18650-li-ion-cell-3500mah-flat-top | Samsung 35E 18650 Li-ion Cell, 3500mAh, Flat Top | 1 | $8.70 |  |

---

# Voltaplex Products

## Voltaplex - Battery

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| lg-b4-18650-li-ion-cell-2600mah-3-75a | LG B4 18650 Li-ion Cell, 2600mAh, 3.75A | 1 | — |  |

---

# Home Depot Products

## Home Depot - Accessory

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| general-tools-1-4-in-x-1-13-in-fluted-dowel-pins-72-pcs | General Tools 1/4 in. x 1.13 in. Fluted Dowel Pins (72 pcs) | 1 | $3.28 |  |

---

# Store not recorded Products

## Store not recorded - Microcontroller

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| raspberry-pi-4-model-b | Raspberry Pi 4 Model B | 1 | — |  |
| raspberry-pi-pico-w | Raspberry Pi Pico W | 1 | — |  |
| waveshare-rp2040-pizero | Waveshare RP2040-PiZero | 1 | — |  |
| waveshare-rp2040-plus | Waveshare RP2040-Plus | 1 | — |  |
| yd-rp2040-rp2040-development-board-black | YD-RP2040 RP2040 Development Board (black) | 1 | — |  |

## Store not recorded - Sensor

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| adafruit-vl53l1x-time-of-flight-distance-sensor-stemma-qt | Adafruit VL53L1X Time of Flight Distance Sensor (STEMMA QT) | 1 | — |  |
| cjmcu-3216-ap3216c-light-and-proximity-sensor | CJMCU-3216 AP3216C Light and Proximity Sensor | 1 | — |  |

## Store not recorded - Display

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| 1602-16x2-character-lcd-with-pcf8574-i2c-backpack-blue | 1602 16x2 Character LCD with PCF8574 I2C Backpack (blue) | 1 | — |  |
| adafruit-rgb-matrix-hat-rtc-for-raspberry-pi | Adafruit RGB Matrix HAT + RTC for Raspberry Pi | 1 | — |  |

## Store not recorded - Breakout Board

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| pimoroni-haptic-bzzz-breakout-drv2605l | Pimoroni Haptic Bzzz Breakout (DRV2605L) | 1 | — |  |

## Store not recorded - FeatherWing

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| adafruit-rgb-matrix-featherwing | Adafruit RGB Matrix FeatherWing | 1 | — |  |

## Store not recorded - Wireless/RF

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| tplink-usb-wifi-adapter | TP-Link USB Wi-Fi Adapter | 1 | — |  |
| waveshare-pico-ble | Waveshare Pico-BLE | 1 | — |  |
| waveshare-pico-can-b | Waveshare Pico-CAN-B | 1 | — |  |
| waveshare-pico-lora-sx126x | Waveshare Pico-LoRa-SX126X | 1 | — |  |

## Store not recorded - Tool

| ID | Product | Qty | Price | Links |
|------|---------|----:|------:|-------|
| DSO2D10 | Hantek DSO2D10 | 1 | — | [Product](https://www.hantek.com/products/detail/17182) · [Guide](https://www.eevblog.com/forum/testgear/hantek-dso2x1x-models-master-thread/) |
| RD6012 | Riden RD6012 | 1 | — | [Product](https://www.banggood.com/RIDEN-RD6012-RD6012W-USB-WiFi-DC-DC-Voltage-Current-Step-Down-Power-Supply-Module-Buck-Voltage-Converter-Voltmeter-60V-12A-p-1687705.html) · [Guide](https://sigrok.org/wiki/RDTech_RD_series) |
