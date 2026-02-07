#!/usr/bin/env python3
"""Generate products.json from purchase_history.csv with pre-populated product data."""
import csv
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Map of product_id -> {description, specifications, learn_guide_url, category}
PRODUCT_DATA = {
    "9": {
        "description": "Super strong neodymium rare earth magnet. Great for holding things together or making magnetic clasps.",
        "specifications": "Type: Neodymium (NdFeB); Shape: Disc; Coating: Nickel plated",
        "learn_guide_url": None,
        "category": "Component"
    },
    "50": {
        "description": "The Adafruit METRO 328 is an ATmega328-based microcontroller board, fully compatible with the Arduino IDE. Features a standard Arduino UNO R3 shield-compatible header layout.",
        "specifications": "Microcontroller: ATmega328P; Clock: 16 MHz; Digital I/O: 20 (6 PWM); Analog Inputs: 6; Flash: 32KB; SRAM: 2KB; EEPROM: 1KB; USB: Micro-B; Voltage: 5V logic",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-metro",
        "category": "Microcontroller"
    },
    "64": {
        "description": "Half-size solderless breadboard with 400 tie points. High quality with nickel-plated contacts and strong adhesive backing.",
        "specifications": "Tie Points: 400; Size: 3.3\" x 2.1\" x 0.33\" (83mm x 54mm x 8.5mm); Rows: 30; Power Rails: 2",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "136": {
        "description": "Ladyada's Electronics Toolkit - a comprehensive set of tools for electronics work including multimeter, soldering iron, wire strippers, pliers, and more.",
        "specifications": "Includes: Multimeter, soldering iron, solder, wire strippers, flush cutters, needle-nose pliers, screwdrivers, helping hands, and more",
        "learn_guide_url": "https://learn.adafruit.com/ladyadas-learn-arduino-lesson-number-0",
        "category": "Tool"
    },
    "151": {
        "description": "Panavise Jr. - a compact and versatile vise for holding PCBs and small parts during soldering and assembly work.",
        "specifications": "Jaw Opening: 2.5\"; Jaw Width: 1.5\"; Base: Weighted; Head: 360° rotation",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "153": {
        "description": "Bundle of pre-cut breadboarding wires in various lengths and colors. Perfect for making neat breadboard circuits.",
        "specifications": "Wire Gauge: 22AWG; Type: Solid core; Colors: Assorted; Lengths: Various (pre-cut)",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "157": {
        "description": "Miniature IR receiver sensor module for detecting 38KHz infrared signals from remote controls.",
        "specifications": "Frequency: 38KHz; Voltage: 3.3-5V; Output: Digital; Wavelength: 940nm; Range: ~10m",
        "learn_guide_url": "https://learn.adafruit.com/ir-sensor",
        "category": "Sensor"
    },
    "159": {
        "description": "Diffused 5mm RGB LED with separate red, green, and blue elements. Common cathode, can produce any color by mixing.",
        "specifications": "Size: 5mm; Type: Common Cathode; Colors: Red/Green/Blue; Forward Voltage: 2.0-3.4V; Max Current: 20mA per channel",
        "learn_guide_url": None,
        "category": "LED"
    },
    "239": {
        "description": "Full-size solderless breadboard with 830 tie points. Premium quality with nickel-plated contacts.",
        "specifications": "Tie Points: 830; Size: 6.5\" x 2.1\"; Rows: 63; Power Rails: 4; Contact: Nickel alloy",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "261": {
        "description": "JST PH 2-pin cable with female connector, 100mm long. Used for battery and power connections on many Adafruit boards.",
        "specifications": "Connector: JST PH 2mm pitch; Pins: 2; Length: 100mm; Wire: 26AWG",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "292": {
        "description": "I2C/SPI character LCD backpack that lets you control a character LCD display over I2C or SPI with just 2 wires. STEMMA QT compatible.",
        "specifications": "Interface: I2C (default) or SPI; Voltage: 5V; Address: 0x20 (default); Compatible: Standard HD44780 LCDs; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/i2c-spi-lcd-backpack",
        "category": "Breakout Board"
    },
    "326": {
        "description": "Monochrome 0.96 inch 128x64 OLED graphic display with STEMMA QT connector. Crisp white pixels on black background.",
        "specifications": "Display: 128x64 pixels; Size: 0.96\"; Interface: I2C; Voltage: 3.3-5V; Driver: SSD1306; Connector: STEMMA QT / Qwiic",
        "learn_guide_url": "https://learn.adafruit.com/monochrome-oled-breakouts",
        "category": "Display"
    },
    "356": {
        "description": "Small breadboard-friendly trim potentiometer for adjusting voltage levels in circuits. 10K ohm resistance.",
        "specifications": "Resistance: 10K Ohm; Type: Single turn trimmer; Pin Spacing: 0.1\" breadboard compatible",
        "learn_guide_url": None,
        "category": "Component"
    },
    "373": {
        "description": "Breadboard-friendly 2.1mm DC barrel jack for easily adding DC power to breadboard projects.",
        "specifications": "Barrel Size: 2.1mm inner / 5.5mm outer; Pin Spacing: 0.1\" breadboard compatible; Max Voltage: 24V DC",
        "learn_guide_url": None,
        "category": "Component"
    },
    "377": {
        "description": "Rotary encoder with extras - a mechanical rotary encoder with built-in pushbutton switch and a nice knurled knob.",
        "specifications": "Type: Mechanical incremental; Detents: 24 per revolution; Switch: Built-in pushbutton; Shaft: 6mm D-shaft",
        "learn_guide_url": "https://learn.adafruit.com/rotary-encoder",
        "category": "Component"
    },
    "380": {
        "description": "CR1220 3V lithium coin cell battery. Used for RTC backup and low-power applications.",
        "specifications": "Type: CR1220; Voltage: 3V; Chemistry: Lithium; Diameter: 12mm; Height: 2.0mm; Capacity: ~40mAh",
        "learn_guide_url": None,
        "category": "Power"
    },
    "398": {
        "description": "RGB backlight positive LCD 16x2 display with extras. Features adjustable RGB backlight to create any color.",
        "specifications": "Display: 16x2 characters; Backlight: RGB (adjustable); Controller: HD44780 compatible; Voltage: 5V; Interface: Parallel",
        "learn_guide_url": "https://learn.adafruit.com/rgb-backlit-lcds",
        "category": "Display"
    },
    "431": {
        "description": "Tiny modular snap boxes for SMD component storage. 10 pack of small snap-together storage compartments.",
        "specifications": "Quantity: 10 pack; Size: Tiny; Material: Plastic; Feature: Snap-together modular design",
        "learn_guide_url": None,
        "category": "Storage"
    },
    "432": {
        "description": "Small modular snap boxes for SMD component storage. 3 pack of snap-together storage compartments.",
        "specifications": "Quantity: 3 pack; Size: Small; Material: Plastic; Feature: Snap-together modular design",
        "learn_guide_url": None,
        "category": "Storage"
    },
    "433": {
        "description": "Medium modular snap boxes for SMD component storage. 2 pack of snap-together storage compartments.",
        "specifications": "Quantity: 2 pack; Size: Medium; Material: Plastic; Feature: Snap-together modular design",
        "learn_guide_url": None,
        "category": "Storage"
    },
    "434": {
        "description": "Large modular snap box for SMD component storage. Snaps together with other boxes in the series.",
        "specifications": "Quantity: 1; Size: Large; Material: Plastic; Feature: Snap-together modular design",
        "learn_guide_url": None,
        "category": "Storage"
    },
    "443": {
        "description": "Large premium solderless breadboard with extra-long power rails and strong adhesive backing.",
        "specifications": "Tie Points: 1660+; Power Rails: Full length; Size: Extra large; Contact: Nickel alloy",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "453": {
        "description": "MAX7219CNG LED matrix/digit display driver IC. Drives up to 8 digits of 7-segment displays or an 8x8 LED matrix via SPI.",
        "specifications": "IC: MAX7219; Interface: SPI; Max Digits: 8 (7-segment); Max LEDs: 64; Package: DIP-24; Voltage: 5V",
        "learn_guide_url": None,
        "category": "Component"
    },
    "455": {
        "description": "Small 1.2 inch 8x8 ultra bright red LED matrix. Commonly used with the HT16K33 LED backpack.",
        "specifications": "Size: 1.2\" (30mm); Matrix: 8x8 (64 LEDs); Color: Red; Forward Voltage: ~2V; Interface: Multiplex",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-led-backpack",
        "category": "LED"
    },
    "480": {
        "description": "Small arcade-style joystick with 4 microswitches for up/down/left/right. Classic arcade feel.",
        "specifications": "Type: 4-way with microswitches; Mounting: Panel mount; Shaft: Removable ball top; Switches: SPDT micro",
        "learn_guide_url": None,
        "category": "Component"
    },
    "669": {
        "description": "ESD (Electrostatic Discharge) warning sticker. Fun and functional static awareness sticker.",
        "specifications": "Type: Vinyl sticker; Theme: ESD warning",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "715": {
        "description": "Adafruit I2C controlled keypad shield kit for 16x2 LCD. Includes 5 navigation buttons and a 16x2 character LCD.",
        "specifications": "Display: 16x2 character LCD; Interface: I2C; Buttons: 5 (Select, Up, Down, Left, Right); Voltage: 5V; Shield: Arduino UNO compatible",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-i2c-controlled-keypad-shield-for-16x2-lcd",
        "category": "Display"
    },
    "727": {
        "description": "3xAAA battery holder with on/off switch and 2-pin JST PH connector. Perfect for portable projects.",
        "specifications": "Batteries: 3x AAA; Voltage: 4.5V (3x1.5V); Connector: JST PH 2-pin; Feature: On/Off slide switch; Lead Length: ~6\"",
        "learn_guide_url": None,
        "category": "Power"
    },
    "735": {
        "description": "74LVC245 breadboard-friendly 8-bit logic level shifter. Shifts between 3.3V and 5V logic levels bidirectionally.",
        "specifications": "IC: 74LVC245; Channels: 8-bit; Direction: Bidirectional; Voltage: 1.65V-5.5V; Package: DIP; Breadboard friendly",
        "learn_guide_url": None,
        "category": "Component"
    },
    "757": {
        "description": "4-channel I2C-safe bidirectional logic level converter. Safely steps between 3.3V and 5V logic on I2C and other buses.",
        "specifications": "Channels: 4; Direction: Bidirectional; Low Side: 1.8-3.3V; High Side: 3.3-5V; Safe for: I2C, SPI, UART",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-4-channel-adc-breakouts",
        "category": "Breakout Board"
    },
    "758": {
        "description": "Premium male/male jumper wires, 40 wires x 6 inches (150mm). Color-coded for easy identification.",
        "specifications": "Quantity: 40; Length: 6\" (150mm); Type: Male/Male; Gauge: 24AWG; Colors: Rainbow assorted",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "759": {
        "description": "Premium male/male jumper wires, 40 wires x 3 inches (75mm). Short length for compact breadboard circuits.",
        "specifications": "Quantity: 40; Length: 3\" (75mm); Type: Male/Male; Gauge: 24AWG; Colors: Rainbow assorted",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "760": {
        "description": "Premium male/male jumper wires, 40 wires x 12 inches (300mm). Extra long for larger projects.",
        "specifications": "Quantity: 40; Length: 12\" (300mm); Type: Male/Male; Gauge: 24AWG; Colors: Rainbow assorted",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "805": {
        "description": "Breadboard-friendly SPDT slide switch. Small form factor that plugs directly into a breadboard.",
        "specifications": "Type: SPDT (Single Pole Double Throw); Rating: 0.3A at 30VDC; Pin Spacing: 0.1\" breadboard compatible",
        "learn_guide_url": None,
        "category": "Component"
    },
    "860": {
        "description": "Miniature 8x8 yellow LED matrix display, 0.8 inch size. Great for small indicator displays.",
        "specifications": "Size: 0.8\" (20mm); Matrix: 8x8 (64 LEDs); Color: Yellow; Interface: Multiplex row/column",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-led-backpack",
        "category": "LED"
    },
    "877": {
        "description": "Adafruit 7-segment LED matrix backpack with STEMMA QT connector. I2C-controlled 4-digit 7-segment display driver.",
        "specifications": "Driver: HT16K33; Interface: I2C; Address: 0x70 (configurable); Digits: 4x 7-segment; Voltage: 5V; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-led-backpack",
        "category": "Display"
    },
    "904": {
        "description": "INA219 high-side DC current sensor breakout board. Measures current and voltage over I2C with 1% precision.",
        "specifications": "Sensor: INA219; Interface: I2C; Max Voltage: 26V; Max Current: ±3.2A; Resolution: 0.8mA; Accuracy: 1%; Connector: STEMMA QT compatible",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout",
        "category": "Sensor"
    },
    "905": {
        "description": "Large plastic project enclosure, weatherproof with clear top. IP65 rated for outdoor projects.",
        "specifications": "Size: 6.3\" x 6.3\" x 3.5\" (160x160x90mm); Rating: IP65 weatherproof; Material: ABS plastic; Top: Clear polycarbonate",
        "learn_guide_url": None,
        "category": "Enclosure"
    },
    "954": {
        "description": "USB to TTL serial cable for Raspberry Pi debug/console. Connects to Pi's UART pins for serial terminal access.",
        "specifications": "Interface: USB to TTL UART; Chipset: PL2303HX; Voltage: 3.3V logic; Baud: Up to 115200; Connector: USB-A to bare wires",
        "learn_guide_url": "https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable",
        "category": "Cable/Connector"
    },
    "1009": {
        "description": "Colorful round tactile button switch assortment. 15 pack of 6mm round pushbuttons in various colors.",
        "specifications": "Quantity: 15; Shape: Round; Size: 6mm; Type: Momentary tactile; Colors: Assorted; Pin Spacing: Breadboard compatible",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1010": {
        "description": "Colorful 12mm square tactile button switch assortment. 15 pack of square pushbuttons in various colors.",
        "specifications": "Quantity: 15; Shape: Square; Size: 12mm; Type: Momentary tactile; Colors: Assorted",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1048": {
        "description": "Adafruit 1.2 inch 8x8 LED matrix backpack. I2C-controlled HT16K33 driver board for 8x8 LED matrices.",
        "specifications": "Driver: HT16K33; Interface: I2C; Address: 0x70 (configurable); Matrix: 8x8; Voltage: 5V; Size: 1.2\"",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-led-backpack",
        "category": "Display"
    },
    "1074": {
        "description": "Configurable spring terminal blocks, 3-pin 0.1 inch pitch, right angle. 5 pack for PCB connections.",
        "specifications": "Quantity: 5; Pins: 3; Pitch: 0.1\" (2.54mm); Type: Right angle; Connection: Spring clamp",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1081": {
        "description": "Configurable spring terminal blocks, 3-pin 0.1 inch pitch, vertical. 5 pack for PCB connections.",
        "specifications": "Quantity: 5; Pins: 3; Pitch: 0.1\" (2.54mm); Type: Vertical; Connection: Spring clamp",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1119": {
        "description": "Tactile switch buttons, 12mm square, 6mm tall. 10 pack of standard pushbutton switches.",
        "specifications": "Quantity: 10; Size: 12mm x 12mm; Height: 6mm; Type: Momentary tactile; Pin Spacing: Breadboard compatible",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1201": {
        "description": "Vibrating mini motor disc. Small pancake vibration motor for haptic feedback in wearables and handheld devices.",
        "specifications": "Type: Pancake/coin; Voltage: 2-3.6V; Current: ~60mA; Diameter: 10mm; Thickness: 2.7mm",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1265": {
        "description": "Yellow 7-segment clock display with 1.2 inch digit height. 4 digits with colon for clock display.",
        "specifications": "Digits: 4 (with colon); Digit Height: 1.2\" (30mm); Color: Yellow; Interface: Multiplex; Common Cathode",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-led-backpack",
        "category": "Display"
    },
    "1312": {
        "description": "Breadboard-friendly RGB smart NeoPixel LEDs. Pack of 5 individually-addressable WS2812B RGB LEDs on breakout PCBs.",
        "specifications": "Quantity: 5; Type: WS2812B (NeoPixel); LED: RGB; Voltage: 5V; Data: Single wire; Breadboard compatible",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-neopixel-uberguide",
        "category": "LED"
    },
    "1328": {
        "description": "2.1mm DC barrel jack to alligator clips cable. Connect a DC power supply to alligator clips.",
        "specifications": "Input: 2.1mm DC barrel jack; Output: Alligator clips (red/black); Length: ~3 feet",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "1399": {
        "description": "RGB 7-segment digit, 1 inch tall. Each segment is individually controllable with RGB color mixing.",
        "specifications": "Digit Height: 1\" (25mm); Type: Common anode RGB; Segments: 7 + decimal; Colors: Full RGB per segment",
        "learn_guide_url": None,
        "category": "LED"
    },
    "1426": {
        "description": "NeoPixel stick with 8x 5050 RGB LEDs with integrated WS2812B drivers. Chainable addressable LED strip.",
        "specifications": "LEDs: 8x WS2812B; Size: 5050; Color: RGB; Voltage: 5V; Dimensions: 2\" x 0.4\"; Chainable: Yes",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-neopixel-uberguide",
        "category": "LED"
    },
    "1431": {
        "description": "OLED breakout board, 16-bit color 1.5 inch display with microSD card holder. Full color OLED with SPI interface.",
        "specifications": "Display: 128x128 pixels; Size: 1.5\"; Color: 16-bit (65K colors); Interface: SPI; Driver: SSD1351; Feature: microSD slot",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-1-5-color-oled-breakout-board",
        "category": "Display"
    },
    "1518": {
        "description": "Adafruit Flex Perma-Proto - a flexible half-sized breadboard PCB made from thin flex material.",
        "specifications": "Size: Half breadboard; Material: Flexible PCB; Layout: Breadboard pattern; Holes: Plated through-hole",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "1528": {
        "description": "Oscilloscope probe rated for 100MHz bandwidth. Standard BNC connector with x1/x10 switch.",
        "specifications": "Bandwidth: 100MHz; Impedance: 1M Ohm; Switch: x1/x10; Connector: BNC; Cable Length: ~4 feet",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "1536": {
        "description": "5V breadboard-friendly buzzer/piezo speaker. Emits a loud tone when powered with 5V.",
        "specifications": "Voltage: 5V; Type: Piezo buzzer; Sound: ~2300Hz; Breadboard compatible; Current: ~30mA",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1592": {
        "description": "Short wire alligator clip test leads, set of 12. Color-coded clips for easy circuit testing.",
        "specifications": "Quantity: 12; Length: Short; Type: Alligator clip to alligator clip; Colors: 6 pairs",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "1597": {
        "description": "Engineer SS-02 professional silicone tip solder sucker. High-quality desoldering pump with replaceable silicone tip.",
        "specifications": "Brand: Engineer; Model: SS-02; Tip: Silicone (heat resistant); Type: Manual vacuum desoldering pump; Tip: Replaceable",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "1598": {
        "description": "Professional IC extraction tool for safely removing DIP ICs from sockets without bending pins.",
        "specifications": "Type: IC extraction/insertion tool; Compatible: DIP packages; Material: Anti-static plastic",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "1609": {
        "description": "Adafruit Perma-Proto half-sized breadboard PCB. Solderable breadboard-layout PCB for making permanent circuits.",
        "specifications": "Size: Half breadboard (3.25\" x 2.15\"); Layout: Breadboard pattern; Holes: Plated through-hole; Material: FR4",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-perma-proto-half-sized-breadboard-pcb",
        "category": "Prototyping"
    },
    "1611": {
        "description": "Silicone elastomer 4x4 button keypad for 3mm LEDs. Translucent silicone pad for the Trellis system.",
        "specifications": "Layout: 4x4 (16 buttons); LED Size: 3mm; Material: Translucent silicone elastomer; Compatible: Adafruit Trellis",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-trellis-diy-open-source-led-keypad",
        "category": "Component"
    },
    "1612": {
        "description": "NeoPixel mini button PCB, pack of 5. Tiny circular PCBs with a single WS2812B NeoPixel LED each.",
        "specifications": "Quantity: 5; LED: WS2812B; Size: ~10mm diameter; Color: RGB; Voltage: 5V; Chainable: Yes",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-neopixel-uberguide",
        "category": "LED"
    },
    "1616": {
        "description": "Adafruit Trellis monochrome driver PCB for 4x4 keypad and 3mm LEDs. HT16K33-based I2C keypad/LED matrix controller.",
        "specifications": "Driver: HT16K33; Interface: I2C; Layout: 4x4; LEDs: 16x 3mm; Buttons: 16 elastomer; Address: Configurable; Tileable: Yes",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-trellis-diy-open-source-led-keypad",
        "category": "Breakout Board"
    },
    "1623": {
        "description": "Small 1.2 inch 8x8 ultra bright pure green LED matrix display.",
        "specifications": "Size: 1.2\" (30mm); Matrix: 8x8 (64 LEDs); Color: Pure Green; Interface: Multiplex",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-led-backpack",
        "category": "LED"
    },
    "1655": {
        "description": "NeoPixel WS2812B 5050 RGB LED with integrated driver chip. 10 pack of loose addressable LEDs.",
        "specifications": "Quantity: 10; Type: WS2812B; Package: 5050 SMD; Color: RGB; Voltage: 5V; Data: Single wire",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-neopixel-uberguide",
        "category": "LED"
    },
    "1661": {
        "description": "uFL (U.FL/IPEX) SMT antenna connector. Tiny surface-mount coaxial RF connector for antenna connections.",
        "specifications": "Type: U.FL / IPEX MHF1; Impedance: 50 Ohm; Mounting: SMT; Frequency: DC-6GHz",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "1683": {
        "description": "On/Off power button pushbutton toggle switch. Latching pushbutton that toggles between on and off states.",
        "specifications": "Type: Latching push-on/push-off; Rating: 3A at 250VAC; Mounting: Panel mount; Thread: 16mm",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1734": {
        "description": "NeoPixel diffused 8mm through-hole LED, 5 pack. Large diffused addressable RGB LEDs with WS2812B driver.",
        "specifications": "Quantity: 5; Size: 8mm; Type: WS2812B; Color: RGB; Voltage: 5V; Lens: Diffused; Through-hole",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-neopixel-uberguide",
        "category": "LED"
    },
    "1754": {
        "description": "Adafruit assembled Pi T-Cobbler breakout for original Raspberry Pi. Connects Pi GPIO to a breadboard via ribbon cable.",
        "specifications": "Compatible: Raspberry Pi Model A/B (26-pin); Connection: Ribbon cable to breadboard; Pins: 26 GPIO",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-pi-t-cobbler",
        "category": "Breakout Board"
    },
    "1766": {
        "description": "Fast vibration sensor switch, easy to trigger. Detects vibration and movement, closes circuit when shaken.",
        "specifications": "Type: Spring vibration switch; Trigger: Easy (sensitive); Output: Normally open; Breadboard compatible",
        "learn_guide_url": None,
        "category": "Sensor"
    },
    "1865": {
        "description": "Edge-launch SMA connector for 1.6mm / 0.062 inch thick PCBs. Standard 50-ohm RF connector.",
        "specifications": "Type: SMA female; Impedance: 50 Ohm; Mounting: Edge-launch PCB; PCB Thickness: 1.6mm (0.062\")",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "1883": {
        "description": "Silicone cover stranded core wire, 2 meters, 26AWG, orange. Flexible and heat-resistant.",
        "specifications": "Length: 2m; Gauge: 26AWG; Color: Orange; Insulation: Silicone; Type: Stranded core",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "1898": {
        "description": "Breadboard-friendly PCB-mount mini speaker. Small 8 Ohm 0.2W speaker that plugs into a breadboard.",
        "specifications": "Impedance: 8 Ohm; Power: 0.2W; Mounting: PCB/breadboard; Diameter: ~25mm",
        "learn_guide_url": None,
        "category": "Component"
    },
    "1950": {
        "description": "Premium female/female jumper wires, 20 wires x 6 inches (150mm). For connecting pin headers.",
        "specifications": "Quantity: 20; Length: 6\" (150mm); Type: Female/Female; Gauge: 24AWG; Colors: Rainbow",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "1953": {
        "description": "Premium female/male extension jumper wires, 20 wires x 3 inches. Extends pin header connections.",
        "specifications": "Quantity: 20; Length: 3\" (75mm); Type: Female/Male; Gauge: 24AWG; Colors: Rainbow",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "2003": {
        "description": "Silicone cover stranded core wire, 2 meters, 30AWG, black. Ultra-flexible thin hookup wire.",
        "specifications": "Length: 2m; Gauge: 30AWG; Color: Black; Insulation: Silicone; Type: Stranded core",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "2005": {
        "description": "Silicone cover stranded core wire, 2 meters, 30AWG, green. Ultra-flexible thin hookup wire.",
        "specifications": "Length: 2m; Gauge: 30AWG; Color: Green; Insulation: Silicone; Type: Stranded core",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "2028": {
        "description": "Assembled Pi T-Cobbler Plus GPIO breakout for Raspberry Pi 2/3/4 with 40-pin connector. Brings all Pi GPIO pins to a breadboard.",
        "specifications": "Compatible: Raspberry Pi 2/3/4/Zero (40-pin); Connection: Ribbon cable to breadboard; Pins: 40 GPIO",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-pi-t-cobbler-plus",
        "category": "Breakout Board"
    },
    "2046": {
        "description": "Potentiometer knob, soft touch T18, red color. Fits standard 6mm D-shaft potentiometers.",
        "specifications": "Color: Red; Shaft: T18 (6mm D-shaft); Material: Soft touch plastic",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "2047": {
        "description": "Potentiometer knob, soft touch T18, white color. Fits standard 6mm D-shaft potentiometers.",
        "specifications": "Color: White; Shaft: T18 (6mm D-shaft); Material: Soft touch plastic",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "2055": {
        "description": "Scrubber knob for rotary encoder, 35mm diameter. Large knob for comfortable scrubbing/scrolling.",
        "specifications": "Diameter: 35mm; Shaft: D-shaft compatible; Material: Plastic; Type: Friction grip",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "2056": {
        "description": "Solid machined metal knob, 1 inch diameter. Premium aluminum knob for potentiometers and encoders.",
        "specifications": "Diameter: 1\" (25mm); Material: Machined aluminum; Shaft: 6mm D-shaft; Finish: Brushed metal",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "2200": {
        "description": "Precision LM4040 voltage reference breakout providing stable 2.048V and 4.096V reference voltages for ADC calibration.",
        "specifications": "IC: LM4040; References: 2.048V and 4.096V; Accuracy: 0.1%; Interface: Analog output; Voltage: 3-15V input",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-lm4040-voltage-reference-breakout",
        "category": "Breakout Board"
    },
    "2305": {
        "description": "Adafruit DRV2605L haptic motor controller breakout with STEMMA QT connector. I2C-controlled driver for vibration motors and LRAs.",
        "specifications": "IC: DRV2605L; Interface: I2C; Effects: 123 built-in; Motor Types: ERM and LRA; Voltage: 3-5V; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-drv2605-haptic-controller-breakout",
        "category": "Breakout Board"
    },
    "2384": {
        "description": "Medium vibration sensor switch. Detects vibration and tilting, moderate sensitivity level.",
        "specifications": "Type: Spring vibration switch; Trigger: Medium sensitivity; Output: Normally open; Breadboard compatible",
        "learn_guide_url": None,
        "category": "Sensor"
    },
    "2476": {
        "description": "Replacement silicone tubes for the Engineer SS-02 professional solder sucker. Pack of replacement tips.",
        "specifications": "Compatible: Engineer SS-02; Material: Silicone; Type: Replacement tip/tube",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "2530": {
        "description": "3W RGB LED with common anode. High-power LED capable of producing bright colors with heat sink recommended.",
        "specifications": "Power: 3W; Type: Common Anode; Colors: Red/Green/Blue; Forward Current: ~350mA per channel; Requires: Heat sink",
        "learn_guide_url": None,
        "category": "LED"
    },
    "2717": {
        "description": "TCA9548A I2C multiplexer breakout. Allows connecting up to 8 I2C devices with the same address to one bus.",
        "specifications": "IC: TCA9548A; Interface: I2C; Channels: 8; Voltage: 3.3-5V; Address: 0x70 (configurable, 8 addresses); Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout",
        "category": "Breakout Board"
    },
    "2739": {
        "description": "Diffused rectangular 5mm RGB LEDs, pack of 10. Common cathode rectangular-shaped RGB LEDs.",
        "specifications": "Quantity: 10; Size: 5mm; Shape: Rectangular/Square; Type: Common Cathode RGB; Lens: Diffused",
        "learn_guide_url": None,
        "category": "LED"
    },
    "2830": {
        "description": "Stacking headers for Adafruit Feather, 12-pin and 16-pin female headers. Allows stacking multiple FeatherWings.",
        "specifications": "Pins: 12-pin + 16-pin; Type: Female stacking; Height: Extra tall; Compatible: Feather ecosystem",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "2884": {
        "description": "FeatherWing Proto - a prototyping add-on board for all Feather boards. Solderable prototype area in Feather form factor.",
        "specifications": "Form Factor: Feather; Type: Prototyping; Holes: Plated through-hole; Compatible: All Feather boards",
        "learn_guide_url": "https://learn.adafruit.com/featherwing-proto-and-doubler",
        "category": "FeatherWing"
    },
    "2888": {
        "description": "BNC male plug to terminal block adapter. Converts BNC to screw terminal connections.",
        "specifications": "Input: BNC male plug; Output: Screw terminal; Impedance: 50 Ohm",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "2889": {
        "description": "BNC female jack to terminal block adapter. Converts BNC to screw terminal connections.",
        "specifications": "Input: BNC female jack; Output: Screw terminal; Impedance: 50 Ohm",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "2900": {
        "description": "Adafruit FeatherWing OLED, 128x32 pixel monochrome display add-on for Feather boards. I2C interface with buttons.",
        "specifications": "Display: 128x32 OLED; Interface: I2C; Buttons: 3 (A, B, C); Driver: SSD1306; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-oled-featherwing",
        "category": "FeatherWing"
    },
    "2922": {
        "description": "Adalogger FeatherWing with RTC and SD card slot. Add data logging capabilities to any Feather board.",
        "specifications": "RTC: PCF8523; Storage: microSD slot; Interface: I2C (RTC) + SPI (SD); Battery: CR1220 backup; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-adalogger-featherwing",
        "category": "FeatherWing"
    },
    "2926": {
        "description": "Assembled terminal block breakout FeatherWing. Brings all Feather pins out to screw terminal blocks for secure connections.",
        "specifications": "Terminals: Screw type; Pins: All Feather pins broken out; Form Factor: FeatherWing; Pre-assembled",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-terminal-block-breakout-featherwing",
        "category": "FeatherWing"
    },
    "2927": {
        "description": "DC Motor + Stepper FeatherWing for all Feather boards. Drive 4 DC motors or 2 stepper motors from a Feather.",
        "specifications": "IC: TB6612; DC Motors: 4 (or 2 steppers); Voltage: 4.5-13.5V motor; PWM: Dedicated; Interface: I2C; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-stepper-dc-motor-featherwing",
        "category": "FeatherWing"
    },
    "2928": {
        "description": "8-Channel PWM or Servo FeatherWing for all Feather boards. Control up to 8 servos or PWM outputs via I2C.",
        "specifications": "IC: PCA9685; Channels: 8; Interface: I2C; PWM: 12-bit resolution; Voltage: 3.3/5V logic; Servo Voltage: External V+; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-8-channel-pwm-or-servo-featherwing",
        "category": "FeatherWing"
    },
    "2940": {
        "description": "Short headers kit for Feather, 12-pin and 16-pin female headers. Low-profile headers for compact stacking.",
        "specifications": "Pins: 12-pin + 16-pin; Type: Female; Height: Short/low-profile; Compatible: Feather ecosystem",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "3002": {
        "description": "Short Feather male headers, 12-pin and 16-pin. For soldering onto Feather boards for breadboard use.",
        "specifications": "Pins: 12-pin + 16-pin; Type: Male; Height: Short; Compatible: Feather ecosystem",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "3019": {
        "description": "Third Hand / Pana-Hand workstation add-on for Panavise. Flexible arms with clips for holding PCBs and components during soldering.",
        "specifications": "Arms: Multiple flexible; Clips: Alligator; Compatible: Panavise bases; Feature: Adjustable positions",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "3067": {
        "description": "AdaBox subscription - quarterly surprise box of electronics, components, and projects from Adafruit.",
        "specifications": "Type: Subscription box; Frequency: Quarterly; Contents: Electronics projects, components, guides",
        "learn_guide_url": "https://learn.adafruit.com/adabox",
        "category": "Book/Subscription"
    },
    "3070": {
        "description": "Adafruit RFM69HCW transceiver radio breakout at 868 or 915 MHz. Long-range packet radio for wireless communication.",
        "specifications": "Chipset: RFM69HCW; Frequency: 868/915 MHz; Range: ~500m (line of sight); Power: Up to +20dBm; Interface: SPI; Modulation: FSK",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts",
        "category": "Breakout Board"
    },
    "3101": {
        "description": "Soft tactile buttons, 8mm, pack of 10. Quiet and soft-press momentary pushbuttons.",
        "specifications": "Quantity: 10; Size: 8mm; Type: Soft tactile momentary; Feel: Quiet, soft press",
        "learn_guide_url": None,
        "category": "Component"
    },
    "3104": {
        "description": "Mini illuminated momentary pushbutton with red power symbol. Lights up when active.",
        "specifications": "Type: Momentary; LED: Red illuminated; Symbol: Power icon; Mounting: Panel mount; Thread: 16mm",
        "learn_guide_url": None,
        "category": "Component"
    },
    "3134": {
        "description": "Adafruit 15x7 CharliePlex LED matrix display FeatherWing in red. Ultra-compact LED matrix for Feather boards.",
        "specifications": "Matrix: 15x7 (105 LEDs); Color: Red; Driver: IS31FL3731; Interface: I2C; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-15x7-7x15-charlieplex-led-matrix-display-featherwing",
        "category": "FeatherWing"
    },
    "3152": {
        "description": "Adafruit 0.8 inch 8x16 LED matrix FeatherWing display in red. Dual 8x8 matrices on a FeatherWing.",
        "specifications": "Matrix: 8x16 (128 LEDs); Size: 0.8\"; Color: Red; Driver: HT16K33; Interface: I2C; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-led-backpack",
        "category": "FeatherWing"
    },
    "3175": {
        "description": "Hook-up wire spool set, 22AWG stranded core, 10 spools x 25ft each in different colors.",
        "specifications": "Gauge: 22AWG; Type: Stranded core; Quantity: 10 spools x 25ft; Colors: 10 different; Total: 250ft",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "3176": {
        "description": "Adafruit Feather M0 RFM69HCW packet radio at 868 or 915 MHz. ATSAMD21 Feather with built-in radio transceiver.",
        "specifications": "MCU: ATSAMD21G18 (ARM Cortex M0+); Clock: 48MHz; Flash: 256KB; RAM: 32KB; Radio: RFM69HCW 868/915MHz; USB: Micro-B; Battery: LiPo charger",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-feather-m0-radio-with-rfm69-packet-radio",
        "category": "Microcontroller"
    },
    "3217": {
        "description": "Maker Paste - low temperature lead-free prototyping solder paste. Easy to use syringe applicator for SMD soldering.",
        "specifications": "Type: Lead-free solder paste; Temperature: Low temp (138°C); Alloy: Sn42/Bi58; Applicator: Syringe",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "3255": {
        "description": "Small alligator clip to male jumper wire bundle, 12 pieces. Connect alligator clips to breadboards.",
        "specifications": "Quantity: 12; Type: Alligator clip to male jumper; Colors: Assorted; Length: ~6\"",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "3299": {
        "description": "Black nylon machine screw and standoff set with M2.5 thread. Assorted lengths for mounting PCBs and projects.",
        "specifications": "Thread: M2.5; Material: Black nylon; Contents: Screws, nuts, standoffs in various lengths; Non-conductive",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "3310": {
        "description": "5.5mm/2.1mm barrel connector DC power plug. Standard size for most DC power adapters.",
        "specifications": "Size: 5.5mm outer / 2.1mm inner; Type: Male plug; Connection: Screw terminal",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "3333": {
        "description": "Circuit Playground Express - an all-in-one electronics learning board with 10 NeoPixels, sensors, buttons, and more. Programmable with MakeCode, CircuitPython, and Arduino.",
        "specifications": "MCU: ATSAMD21G18 (ARM Cortex M0+); Clock: 48MHz; Flash: 256KB; RAM: 32KB; LEDs: 10x NeoPixel RGB; Sensors: Temperature, light, sound (MEMS mic), accelerometer (LIS3DH); Buttons: 2 + slide switch; Speaker: Built-in mini; IR: Transmit and receive; Capacitive Touch: 8 pads; USB: Micro-B",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-circuit-playground-express",
        "category": "Microcontroller"
    },
    "3340": {
        "description": "900MHz antenna kit for LoRa, LoPy, and other sub-GHz radios. Includes antenna and uFL adapter cable.",
        "specifications": "Frequency: 900MHz (868-915MHz); Type: Dipole antenna; Connector: uFL to SMA adapter included; Gain: ~2dBi",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "3417": {
        "description": "FeatherWing Tripler mini kit. Connect three Feather boards together, allowing a Feather and two FeatherWings to share one bus.",
        "specifications": "Slots: 3 (1 Feather + 2 FeatherWings); Assembly: Soldering required; Pins: All Feather pins connected",
        "learn_guide_url": "https://learn.adafruit.com/featherwing-proto-and-doubler",
        "category": "Prototyping"
    },
    "3500": {
        "description": "Adafruit Trinket M0 - tiny ATSAMD21-based microcontroller board for CircuitPython and Arduino. The tiniest Adafruit board.",
        "specifications": "MCU: ATSAMD21E18 (ARM Cortex M0+); Clock: 48MHz; Flash: 256KB; RAM: 32KB; GPIO: 5; USB: Micro-B (native); LED: DotStar RGB; Size: 27mm x 15mm",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino",
        "category": "Microcontroller"
    },
    "3505": {
        "description": "Adafruit METRO M0 Express - ATSAMD21-based board designed for CircuitPython. Arduino UNO form factor with native USB.",
        "specifications": "MCU: ATSAMD21G18 (ARM Cortex M0+); Clock: 48MHz; Flash: 256KB + 2MB SPI; RAM: 32KB; Digital I/O: 25; Analog: 6 in + 1 out; USB: Micro-B (native); LED: NeoPixel",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-metro-m0-express",
        "category": "Microcontroller"
    },
    "3540": {
        "description": "Square 60mm x 60mm soldering sponge, 3 pack. Replacement sponges for soldering iron stands.",
        "specifications": "Quantity: 3; Size: 60mm x 60mm; Material: Cellulose sponge; Use: Soldering iron tip cleaning",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "3585": {
        "description": "Great Scott Gadgets ANT700 telescoping antenna, 300MHz to 1100MHz. Adjustable length for tuning to different frequencies.",
        "specifications": "Frequency: 300-1100MHz; Type: Telescoping; Connector: SMA male; Length: Adjustable; Impedance: 50 Ohm",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "3642": {
        "description": "2.1mm DC power jack with built-in slide switch. Convenient power input with on/off control.",
        "specifications": "Barrel: 2.1mm/5.5mm; Switch: SPDT slide; Rating: 5A; Mounting: Panel or breadboard",
        "learn_guide_url": None,
        "category": "Component"
    },
    "3786": {
        "description": "2-pin wire joints, 3 pack. Quick no-solder wire splice connectors for joining wires.",
        "specifications": "Quantity: 3; Pins: 2; Type: Wire splice joint; Method: No-solder push-in",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "3804": {
        "description": "Large clear practice padlock for lock picking practice. Transparent body shows the pin mechanism.",
        "specifications": "Type: Practice/training padlock; Body: Clear/transparent; Pins: Standard pin tumbler; Feature: Visible mechanism",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "3806": {
        "description": "Basic lock sport pick set with 9 picks and 2 tension wrenches. Starter set for learning lock picking.",
        "specifications": "Picks: 9; Tension Wrenches: 2; Material: Stainless steel; Type: Beginner/basic set",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "3885": {
        "description": "Adafruit STEMMA speaker - plug and play audio amplifier. Simple powered speaker with JST connector for audio output.",
        "specifications": "Amplifier: Class D; Connector: JST PH 3-pin (STEMMA); Power: 3-5V; Audio: Mono; Size: Compact",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-stemma-speaker",
        "category": "Component"
    },
    "3893": {
        "description": "STEMMA JST PH 2mm 3-pin to male header cable, 200mm long. Connects STEMMA 3-pin devices to breadboards.",
        "specifications": "Connector A: JST PH 3-pin; Connector B: Male headers; Length: 200mm; Wire: 26AWG",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "3915": {
        "description": "Adafruit Circuit Playground Express or Bluefruit enclosure. Snap-fit clear case that protects the board while exposing sensors.",
        "specifications": "Compatible: Circuit Playground Express, Bluefruit; Material: Clear plastic; Type: Snap-fit; Feature: Access to buttons, LEDs, sensors",
        "learn_guide_url": None,
        "category": "Enclosure"
    },
    "3954": {
        "description": "Adafruit NeoTrellis RGB driver PCB for 4x4 keypad. I2C-controlled 4x4 elastomer keypad with NeoPixel RGB LEDs.",
        "specifications": "LEDs: 16x NeoPixel (seesaw controlled); Buttons: 4x4 elastomer; Interface: I2C (seesaw); Voltage: 3.3-5V; Tileable: Yes (up to 8)",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-neotrellis",
        "category": "Breakout Board"
    },
    "3988": {
        "description": "Adafruit Prop-Maker FeatherWing - add-on board for building cosplay props, lightsabers, and wands. Includes amplifier, accelerometer, and NeoPixel driver.",
        "specifications": "Features: 3W audio amp, accelerometer (LIS3DH), NeoPixel level-shifter; Power: Servo + high-current output; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-prop-maker-featherwing",
        "category": "FeatherWing"
    },
    "4030": {
        "description": "JST PH 2mm 3-pin plug to color-coded alligator clips cable. Quick prototyping connection.",
        "specifications": "Connector: JST PH 3-pin; Output: 3 alligator clips (color coded); Length: ~12\"",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4036": {
        "description": "DIY ornament kit, 6cm diameter, perfect for Circuit Playground. Clear plastic ornament ball for holiday decorations.",
        "specifications": "Diameter: 6cm; Material: Clear plastic; Compatible: Circuit Playground; Type: 2-piece snap-together",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "4042": {
        "description": "Diffused red and green indicator LED, 18mm round. Bi-color LED indicator light with built-in resistor.",
        "specifications": "Size: 18mm; Colors: Red/Green; Type: Bi-color diffused; Voltage: 5-12V (built-in resistor); Current: ~20mA",
        "learn_guide_url": None,
        "category": "LED"
    },
    "4046": {
        "description": "JST PH 2mm 3-pin socket to color-coded cable, 200mm. For connecting to STEMMA 3-pin ports.",
        "specifications": "Connector: JST PH 3-pin socket; Output: Color coded bare wires; Length: 200mm",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4081": {
        "description": "Flat vibration switch, breadboard-friendly. Low-profile vibration/tilt sensor that plugs into a breadboard.",
        "specifications": "Type: Flat vibration switch; Profile: Low/flat; Output: Normally open; Breadboard compatible",
        "learn_guide_url": None,
        "category": "Sensor"
    },
    "4103": {
        "description": "Bolt-on kit for Circuit Playground, micro:bit, Flora, or Gemma. M3 bolts and nuts for secure attachment.",
        "specifications": "Hardware: M3 bolts and nuts; Compatible: Circuit Playground, micro:bit, Flora, Gemma; Material: Nylon",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "4147": {
        "description": "Adafruit ADXL343 + ADT7410 sensor FeatherWing. Accelerometer and precision temperature sensor combo on a FeatherWing.",
        "specifications": "Accelerometer: ADXL343 (±2/4/8/16g); Temperature: ADT7410 (±0.5°C accuracy); Interface: I2C; Form Factor: FeatherWing; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-adxl343-adt7410-sensor-featherwing",
        "category": "FeatherWing"
    },
    "4154": {
        "description": "Break-away 0.1 inch 36-pin strip male header, rainbow combo 10 pack. Color-coded headers for easy identification.",
        "specifications": "Quantity: 10 strips; Pins: 36 per strip; Pitch: 0.1\" (2.54mm); Type: Male; Colors: Rainbow assorted; Break-away",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "4160": {
        "description": "20-pin 0.1 inch female headers, rainbow color mix, 5 pack. Colorful female headers for pin connections.",
        "specifications": "Quantity: 5; Pins: 20 per header; Pitch: 0.1\" (2.54mm); Type: Female; Colors: Rainbow mix",
        "learn_guide_url": None,
        "category": "Prototyping"
    },
    "4203": {
        "description": "Diffused 5mm LED pack with 5 LEDs each in 5 colors, 25 pack total. Standard through-hole LEDs.",
        "specifications": "Quantity: 25 (5 each of 5 colors); Size: 5mm; Colors: Red, Yellow, Green, Blue, White; Lens: Diffused",
        "learn_guide_url": None,
        "category": "LED"
    },
    "4209": {
        "description": "STEMMA QT / Qwiic JST SH 4-pin to premium male headers cable. Connects STEMMA QT devices to breadboards.",
        "specifications": "Connector A: JST SH 4-pin; Connector B: Male pin headers; Length: ~150mm; Wire: 28AWG; Compatible: STEMMA QT / Qwiic",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4210": {
        "description": "STEMMA QT / Qwiic JST SH 4-pin cable, 100mm long. Connects two STEMMA QT / Qwiic devices together.",
        "specifications": "Connector: JST SH 4-pin (both ends); Length: 100mm; Wire: 28AWG; Compatible: STEMMA QT / Qwiic",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4220": {
        "description": "Learn CircuitPython with 1 month subscription to Codecademy Pro. Online coding course access.",
        "specifications": "Type: Digital subscription; Duration: 1 month; Platform: Codecademy Pro; Topic: CircuitPython",
        "learn_guide_url": "https://learn.adafruit.com/welcome-to-circuitpython",
        "category": "Book/Subscription"
    },
    "4227": {
        "description": "Mini oval speaker with short wires, 8 Ohm 1 Watt. Small speaker for audio projects and alerts.",
        "specifications": "Impedance: 8 Ohm; Power: 1W; Shape: Oval; Size: Mini; Wires: Short leads",
        "learn_guide_url": None,
        "category": "Component"
    },
    "4263": {
        "description": "4-H Circuit Playground Express base kit. Includes Circuit Playground Express, USB cable, battery pack, and alligator clips for 4-H learning.",
        "specifications": "Includes: Circuit Playground Express, USB cable, AAA battery pack, alligator clips; Purpose: 4-H education",
        "learn_guide_url": "https://learn.adafruit.com/4-h-circuit-playground-express-base-kit",
        "category": "Kit"
    },
    "4269": {
        "description": "Simple spring antenna for 915MHz. Wire antenna for sub-GHz radio applications.",
        "specifications": "Frequency: 915MHz; Type: Helical spring; Connector: Solder; Size: ~28mm",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "4271": {
        "description": "Slide potentiometer with plastic knob, 35mm long travel, 10K Ohm. Linear sliding control for projects.",
        "specifications": "Resistance: 10K Ohm; Travel: 35mm; Type: Linear slide; Knob: Plastic; Taper: Linear (B)",
        "learn_guide_url": None,
        "category": "Component"
    },
    "4286": {
        "description": "Adafruit DS3502 I2C digital 10K potentiometer breakout. Digitally controlled potentiometer over I2C.",
        "specifications": "IC: DS3502; Resistance: 10K Ohm; Resolution: 7-bit (128 steps); Interface: I2C; Voltage: 3.3-5V; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/ds3502-i2c-potentiometer",
        "category": "Breakout Board"
    },
    "4287": {
        "description": "3.5mm/1.1mm to 5.5mm/2.1mm DC jack adapter. Converts between common DC barrel jack sizes.",
        "specifications": "Input: 3.5mm/1.1mm; Output: 5.5mm/2.1mm; Type: Adapter plug",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4351": {
        "description": "Adafruit Infineon Trust M breakout board with STEMMA QT. Hardware security element for cryptographic operations.",
        "specifications": "IC: Infineon OPTIGA Trust M; Interface: I2C; Features: ECC-256/384, RSA-1024/2048, SHA-256, AES-128; Voltage: 3.3V; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-infineon-trust-m-breakout",
        "category": "Breakout Board"
    },
    "4354": {
        "description": "Adafruit Perma-Proto 40-pin Raspberry Pi breadboard PCB kit. Solderable prototyping board matching Pi's GPIO layout.",
        "specifications": "Layout: Raspberry Pi 40-pin GPIO compatible; Size: HAT form factor; Holes: Plated through-hole; Material: FR4",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-perma-proto-raspberry-pi-pcb",
        "category": "Prototyping"
    },
    "4397": {
        "description": "STEMMA QT / Qwiic JST SH 4-pin cable with premium female sockets. Connect STEMMA QT to female headers.",
        "specifications": "Connector A: JST SH 4-pin; Connector B: Female sockets; Length: ~150mm; Compatible: STEMMA QT / Qwiic",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4398": {
        "description": "JST SH 4-pin cable with alligator clips, STEMMA QT / Qwiic compatible. For quick prototyping connections.",
        "specifications": "Connector: JST SH 4-pin; Output: 4 alligator clips (color coded); Length: ~12\"; Compatible: STEMMA QT / Qwiic",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4399": {
        "description": "STEMMA QT / Qwiic JST SH 4-pin cable, 50mm long. Short cable for close-together STEMMA QT devices.",
        "specifications": "Connector: JST SH 4-pin (both ends); Length: 50mm; Wire: 28AWG; Compatible: STEMMA QT / Qwiic",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4401": {
        "description": "STEMMA QT / Qwiic JST SH 4-pin cable, 200mm long. Medium-length cable for STEMMA QT connections.",
        "specifications": "Connector: JST SH 4-pin (both ends); Length: 200mm; Wire: 28AWG; Compatible: STEMMA QT / Qwiic",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4483": {
        "description": "5-pin JST ESLOV to 4-pin JST SH STEMMA QT / Qwiic cable. Adapter between Arduino ESLOV and STEMMA QT ecosystems.",
        "specifications": "Connector A: JST ESLOV 5-pin; Connector B: JST SH 4-pin (STEMMA QT); Length: ~100mm",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4528": {
        "description": "Grove to STEMMA QT / Qwiic / JST SH cable. Adapter cable between Seeed Grove and Adafruit STEMMA QT ecosystems.",
        "specifications": "Connector A: Grove (4-pin HY2.0); Connector B: JST SH 4-pin (STEMMA QT); Length: ~100mm",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "4559": {
        "description": "Pre-cut multi-colored heat shrink pack kit, 280 pieces. Assorted sizes and colors for wire insulation.",
        "specifications": "Quantity: 280 pieces; Sizes: Assorted (various diameters); Colors: Multi-colored; Shrink Ratio: 2:1",
        "learn_guide_url": None,
        "category": "Tool"
    },
    "4565": {
        "description": "Adafruit LSM6DSOX + LIS3MDL FeatherWing - precision 9-DoF IMU. Accelerometer, gyroscope, and magnetometer combo.",
        "specifications": "Accel/Gyro: LSM6DSOX; Magnetometer: LIS3MDL; DoF: 9 (3-axis accel + 3-axis gyro + 3-axis mag); Interface: I2C/SPI; Form Factor: FeatherWing; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/st-9-dof-combo",
        "category": "FeatherWing"
    },
    "4566": {
        "description": "Adafruit AHT20 temperature and humidity sensor breakout board. Simple I2C sensor with STEMMA QT connector.",
        "specifications": "Sensor: AHT20; Temperature: ±0.3°C accuracy; Humidity: ±2% RH; Interface: I2C; Voltage: 3.3-5V; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-aht20",
        "category": "Sensor"
    },
    "4582": {
        "description": "Finger pulse oximeter with Bluetooth LE. Measures blood oxygen saturation (SpO2) and heart rate wirelessly.",
        "specifications": "Measures: SpO2 and heart rate; Connectivity: Bluetooth LE; Display: OLED; Power: 2x AAA batteries; Feature: BLE data streaming",
        "learn_guide_url": "https://learn.adafruit.com/bluetooth-le-finger-pulse-oximeter",
        "category": "Sensor"
    },
    "4594": {
        "description": "Black LED diffusion acrylic panel, 12x12 inches, 0.1 inch (2.6mm) thick. Diffuses LED light evenly.",
        "specifications": "Size: 12\" x 12\"; Thickness: 0.1\" (2.6mm); Color: Black (diffusing); Material: Acrylic; Use: LED matrix diffusion",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "4600": {
        "description": "Adafruit QT Py - SAMD21 dev board with STEMMA QT connector. Tiny but powerful board for CircuitPython and Arduino.",
        "specifications": "MCU: ATSAMD21E18 (ARM Cortex M0+); Clock: 48MHz; Flash: 256KB; RAM: 32KB; GPIO: 11; USB: USB-C; Connector: STEMMA QT; Size: 0.85\" x 0.7\"",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-qt-py",
        "category": "Microcontroller"
    },
    "4631": {
        "description": "Mini magnet feet for RGB LED matrices, pack of 4. Magnetic mounting feet for LED panels.",
        "specifications": "Quantity: 4; Type: Magnetic feet; Compatible: RGB LED matrices; Material: Rubber + magnet",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "4650": {
        "description": "Adafruit FeatherWing OLED, 128x64 pixel monochrome display add-on for Feather boards. Larger OLED with buttons.",
        "specifications": "Display: 128x64 OLED; Interface: I2C; Buttons: 3 (A, B, C); Driver: SH1107; Form Factor: FeatherWing; Size: 1.0\"",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-128x64-oled-featherwing",
        "category": "FeatherWing"
    },
    "4677": {
        "description": "Generic 64 Mbit serial pseudo-SRAM (PSRAM), 3.3V 133MHz. Additional RAM for microcontroller projects.",
        "specifications": "Capacity: 64 Mbit (8MB); Interface: SPI/QSPI; Voltage: 3.3V; Speed: 133MHz; Package: SOP-8",
        "learn_guide_url": None,
        "category": "Component"
    },
    "4681": {
        "description": "Adafruit BH1750 light sensor breakout with STEMMA QT connector. Digital ambient light intensity sensor.",
        "specifications": "Sensor: BH1750; Range: 1-65535 lux; Interface: I2C; Resolution: 16-bit; Voltage: 3.3-5V; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor",
        "category": "Sensor"
    },
    "4763": {
        "description": "GD25Q16 2MB SPI flash memory in 8-pin SOIC package. External flash storage for microcontrollers.",
        "specifications": "Capacity: 2MB (16 Mbit); Interface: SPI; Speed: 120MHz; Package: 8-pin SOIC; Voltage: 2.7-3.6V",
        "learn_guide_url": None,
        "category": "Component"
    },
    "4813": {
        "description": "Clear adhesive squares, 6 pack. Sticky mounting squares for attaching components and boards.",
        "specifications": "Quantity: 6; Type: Clear adhesive mounting squares; Feature: Removable/repositionable",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "4871": {
        "description": "Breadboard-friendly mini PIR motion sensor with 3-pin header. Compact passive infrared sensor for detecting movement.",
        "specifications": "Type: Passive Infrared (PIR); Range: ~3m; Angle: ~120°; Output: Digital; Voltage: 3.3-5V; Pin Spacing: 0.1\" breadboard compatible",
        "learn_guide_url": "https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor",
        "category": "Sensor"
    },
    "4884": {
        "description": "Adafruit Feather RP2040 - Raspberry Pi RP2040-based Feather board. Dual-core ARM Cortex M0+ with tons of RAM.",
        "specifications": "MCU: RP2040 (Dual ARM Cortex M0+); Clock: 133MHz; Flash: 8MB QSPI; RAM: 264KB; GPIO: 21; USB: USB-C; Battery: LiPo charger; LED: NeoPixel; STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-feather-rp2040-pico",
        "category": "Microcontroller"
    },
    "4886": {
        "description": "Adafruit AW9523 GPIO expander and LED driver breakout. Add 16 extra GPIO pins or LED channels over I2C.",
        "specifications": "IC: AW9523B; GPIO: 16 pins; Interface: I2C; LED Drive: 256-step (8-bit) per pin; Voltage: 3.3V; Max Current: 37mA per pin; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-aw9523-gpio-expander-and-led-driver",
        "category": "Breakout Board"
    },
    "4991": {
        "description": "Adafruit I2C STEMMA QT rotary encoder breakout with NeoPixel. Connects a rotary encoder via I2C with RGB LED feedback.",
        "specifications": "Controller: seesaw (ATSAMD09); Interface: I2C; Features: Encoder input, NeoPixel, interrupt; Voltage: 3.3-5V; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-i2c-qt-rotary-encoder",
        "category": "Breakout Board"
    },
    "5001": {
        "description": "ANO directional navigation and scroll wheel rotary encoder. Multi-function input with scroll, click, and D-pad directions.",
        "specifications": "Functions: Scroll wheel + center click + Up/Down/Left/Right; Type: Mechanical; Interface: Digital; Size: Thumbwheel form factor",
        "learn_guide_url": "https://learn.adafruit.com/ano-rotary-encoder",
        "category": "Component"
    },
    "5036": {
        "description": "64x32 RGB LED matrix panel with 2.5mm pixel pitch. Full-color LED display panel driven via HUB75 interface.",
        "specifications": "Resolution: 64x32 pixels; Pitch: 2.5mm; Colors: RGB (full color); Interface: HUB75; Size: 160mm x 80mm; Voltage: 5V; Scan: 1/16",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-matrixportal-m4",
        "category": "Display"
    },
    "5051": {
        "description": "Black anodized aluminum bumper feet, pack of 2. Adhesive rubber feet for enclosures and projects.",
        "specifications": "Quantity: 2; Material: Anodized aluminum + rubber; Color: Black; Mounting: Adhesive",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "5056": {
        "description": "Adafruit Trinkey QT2040 - RP2040 USB key with STEMMA QT. Plugs directly into USB-A port, has a STEMMA QT connector for I2C devices.",
        "specifications": "MCU: RP2040 (Dual ARM Cortex M0+); Clock: 133MHz; Flash: 8MB QSPI; RAM: 264KB; USB: USB-A (plug-in); Connector: STEMMA QT; LED: NeoPixel; Touch: 1 capacitive pad",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-trinkey-qt2040",
        "category": "Microcontroller"
    },
    "5093": {
        "description": "Slim rubber rotary encoder knob, 11.5mm x 14.5mm, D-shaft. Low-profile knob for encoders and pots.",
        "specifications": "Diameter: 11.5mm; Height: 14.5mm; Shaft: D-shaft (6mm); Material: Rubber; Color: Black",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "5128": {
        "description": "Adafruit MacroPad RP2040 starter kit - 3x4 mechanical keys, rotary encoder, and OLED. Programmable macro keyboard.",
        "specifications": "MCU: RP2040; Keys: 12 (3x4 mechanical); Encoder: Rotary with click; Display: 128x64 OLED; LEDs: 12x NeoPixel (per-key); USB: USB-C; Audio: Speaker",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-macropad-rp2040",
        "category": "Kit"
    },
    "5142": {
        "description": "SparkFun Qwiic pHAT v2.0 for Raspberry Pi. Adds four STEMMA QT / Qwiic connectors to a Raspberry Pi.",
        "specifications": "Connectors: 4x STEMMA QT/Qwiic; Compatible: Raspberry Pi (40-pin); Interface: I2C; Form Factor: pHAT",
        "learn_guide_url": None,
        "category": "Breakout Board"
    },
    "5154": {
        "description": "Digi-Key Innovation Handbook - a reference book covering electronics fundamentals and maker projects.",
        "specifications": "Type: Physical book; Publisher: Digi-Key; Topic: Electronics and innovation",
        "learn_guide_url": None,
        "category": "Book/Subscription"
    },
    "5188": {
        "description": "Adafruit DS3231 precision RTC with STEMMA QT. Extremely accurate real-time clock with temperature-compensated crystal.",
        "specifications": "IC: DS3231; Accuracy: ±2ppm (±1 min/year); Interface: I2C; Battery: CR1220 backup; Voltage: 3.3-5V; Connector: STEMMA QT; Alarm: 2 alarms",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-ds3231-precision-rtc-breakout",
        "category": "Breakout Board"
    },
    "5195": {
        "description": "Etched glow-through keycap with LGTM (Looks Good To Me) acronym. Custom mechanical keyboard keycap.",
        "specifications": "Type: Mechanical keycap; Legend: LGTM; Feature: Glow-through (backlit compatible); Mount: MX compatible",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "5221": {
        "description": "Adafruit ANO rotary navigation encoder breakout PCB. Breakout board for the ANO scroll wheel encoder.",
        "specifications": "Compatible: ANO Rotary Navigation Encoder; Connections: Breakout pads; Mounting: PCB; Interface: Digital GPIO",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-ano-rotary-navigation-encoder-breakout",
        "category": "Breakout Board"
    },
    "5244": {
        "description": "Grove cable pigtail, 2mm pitch, 100mm long. Grove connector on one end, bare wires on other.",
        "specifications": "Connector: Grove (HY2.0 4-pin); Output: Bare wire pigtail; Length: 100mm; Pitch: 2mm",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "5302": {
        "description": "Adafruit KB2040 - RP2040 Kee Boar Driver. Arduino Pro Micro form factor board with RP2040 for mechanical keyboards.",
        "specifications": "MCU: RP2040 (Dual ARM Cortex M0+); Clock: 133MHz; Flash: 8MB QSPI; RAM: 264KB; USB: USB-C; Form Factor: Pro Micro; LED: NeoPixel; STEMMA QT; GPIO: 18",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-kb2040",
        "category": "Microcontroller"
    },
    "5348": {
        "description": "Adafruit QT Py ESP32-S2 WiFi dev board with uFL antenna port. Tiny WiFi-enabled board with STEMMA QT.",
        "specifications": "MCU: ESP32-S2 (240MHz Xtensa); Flash: 4MB + 2MB PSRAM; WiFi: 802.11 b/g/n; USB: USB-C (native); Connector: STEMMA QT + uFL; GPIO: 11; LED: NeoPixel",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-qt-py-esp32-s2",
        "category": "Microcontroller"
    },
    "5358": {
        "description": "DIY magnetic connector with right-angle four contact pins. Magnetic pogo pin connector for detachable connections.",
        "specifications": "Pins: 4; Type: Magnetic pogo pin; Angle: Right angle; Current: Up to 3A; Feature: Snap-on magnetic",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "5412": {
        "description": "Magnetic USB charging cable for 4-pin 0.1 inch magnetic connector. Pairs with DIY magnetic connector.",
        "specifications": "Interface: USB to 4-pin magnetic; Compatible: Adafruit magnetic connectors; Feature: Magnetic snap-on; Cable: USB-A",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "5444": {
        "description": "RP-SMA to w.FL/MHF3/IPEX3 adapter cable. Converts between RP-SMA antenna connector and miniature w.FL/IPEX3.",
        "specifications": "Connector A: RP-SMA; Connector B: w.FL/MHF3/IPEX3; Impedance: 50 Ohm; Type: Adapter pigtail",
        "learn_guide_url": None,
        "category": "Cable/Connector"
    },
    "5527": {
        "description": "Anodized aluminum machined knob, black, 20mm diameter. Premium metal knob for potentiometers and encoders.",
        "specifications": "Diameter: 20mm; Material: Anodized aluminum; Color: Black; Shaft: 6mm D-shaft",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "5531": {
        "description": "Anodized aluminum machined knob, gold, 20mm diameter. Premium metal knob for potentiometers and encoders.",
        "specifications": "Diameter: 20mm; Material: Anodized aluminum; Color: Gold; Shaft: 6mm D-shaft",
        "learn_guide_url": None,
        "category": "Accessory"
    },
    "5625": {
        "description": "Adafruit Qwiic / STEMMA QT 5-port hub. Expands one STEMMA QT / Qwiic port into five for connecting multiple I2C devices.",
        "specifications": "Ports: 5x STEMMA QT/Qwiic; Type: I2C hub (passive); Voltage: 3.3V; No active components (just wired in parallel)",
        "learn_guide_url": None,
        "category": "Breakout Board"
    }
}


def main():
    csv_path = SCRIPT_DIR / "purchase_history.csv"
    json_path = SCRIPT_DIR / "products.json"

    # Read CSV to get order info
    products = {}
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            pid = row["product id"].strip()
            name = row["product name"].strip()
            qty = int(row["quantity"].strip())
            order = row["order"].strip()
            price = float(row["price"].strip())

            if pid in products:
                products[pid]["total_qty"] += qty
                if order not in products[pid]["orders"]:
                    products[pid]["orders"].append(order)
            else:
                products[pid] = {
                    "product_id": pid,
                    "csv_name": name,
                    "total_qty": qty,
                    "orders": [order],
                    "unit_price": price,
                }

    # Build full product data
    output = {}
    for pid in sorted(products.keys(), key=lambda x: int(x)):
        csv_info = products[pid]
        extra = PRODUCT_DATA.get(pid, {})

        output[pid] = {
            "product_id": pid,
            "name": extra.get("description", "").split(".")[0] if extra.get("description") else csv_info["csv_name"],
            "csv_name": csv_info["csv_name"],
            "description": extra.get("description", ""),
            "technical_specs": extra.get("specifications", ""),
            "category": extra.get("category", "Uncategorized"),
            "page_url": f"https://www.adafruit.com/product/{pid}",
            "image_url": f"https://cdn-shop.adafruit.com/970x728/{pid}-00.jpg",
            "learn_guide_url": extra.get("learn_guide_url"),
            "unit_price": csv_info["unit_price"],
            "total_qty": csv_info["total_qty"],
            "orders": csv_info["orders"],
            "last_scraped": None,
        }
        # Use csv_name as the display name (it's the real product name)
        output[pid]["name"] = csv_info["csv_name"]

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    print(f"Generated {len(output)} products in {json_path}")


if __name__ == "__main__":
    main()
