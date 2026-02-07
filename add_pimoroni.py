#!/usr/bin/env python3
"""Add Pimoroni products to products.json."""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

PIMORONI_PRODUCTS = [
    {"code": "PIM373", "name": "VL53L1X Time of Flight (ToF) Sensor Breakout", "qty": 1, "price": 8.90},
    {"code": "PIM301", "name": "Button SHIM", "qty": 1, "price": 4.50},
    {"code": "PIM449", "name": "RV3028 Real-Time Clock (RTC) Breakout", "qty": 1, "price": 7.50},
    {"code": "PIM575", "name": "BME688 4-in-1 Air Quality Breakout (Gas, Temperature, Pressure, Humidity)", "qty": 1, "price": 12.05},
    {"code": "BOB-19389", "name": "SparkFun Analog MEMS Microphone Breakout - SPH8878LR5H-1", "qty": 1, "price": 4.55},
    {"code": "COM0216", "name": "Optoisolator - 1 Channel", "qty": 1, "price": 0.55},
    {"code": "PA-21", "name": "Engineer Universal Crimping Pliers", "qty": 1, "price": 26.00},
    {"code": "COM0005", "name": "Pico Stacking Header Pack", "qty": 3, "price": 0.75},
    {"code": "COM1117", "name": "Pico Header Pack", "qty": 3, "price": 0.90},
    {"code": "ADA1207", "name": "Adafruit SMT breakout PCB for SOIC or TSSOP - 16 pin - pack of three", "qty": 1, "price": 2.75},
    {"code": "ADA1211", "name": "Adafruit SMT breakout PCB for SOIC or TSSOP - 12 pin - pack of six", "qty": 1, "price": 3.40},
    {"code": "PIM479", "name": "DRV8830 DC Motor Driver Breakout", "qty": 1, "price": 5.40},
    {"code": "PIM442", "name": "11x7 LED Matrix Breakout", "qty": 1, "price": 6.25},
    {"code": "PIM435", "name": "5x5 RGB Matrix Breakout", "qty": 1, "price": 4.10},
    {"code": "PIM517", "name": "IO Expander Breakout", "qty": 1, "price": 4.20},
    {"code": "PIM438", "name": "MAX30101 Breakout - Heart Rate, Oximeter, Smoke Sensor", "qty": 1, "price": 8.90},
    {"code": "COM3900", "name": "Breakout Garden I2C Connector (pack of 5)", "qty": 1, "price": 2.35},
    {"code": "PIM572", "name": "Breakout Garden to STEMMA QT / Qwiic Adapter", "qty": 4, "price": 0.80},
    {"code": "PIM455", "name": "HT0740 40V / 10A Switch Breakout", "qty": 1, "price": 11.75},
    {"code": "ADA5664", "name": "Adafruit PCA9546 4-Channel STEMMA QT / Qwiic I2C Multiplexer", "qty": 1, "price": 3.50},
    {"code": "PIM699", "name": "NVMe Base for Raspberry Pi 5", "qty": 1, "price": 11.25},
    {"code": "PIM560", "name": "Pimoroni Pico LiPo - 16MB", "qty": 1, "price": 11.25},
    {"code": "POL-3781", "name": "Step-Down Voltage Regulator D36V28Fx - 3.3V 3.6A", "qty": 1, "price": 6.55},
    {"code": "ADA4258", "name": "Adafruit LPS35HW Water Resistant Pressure Sensor - STEMMA QT", "qty": 1, "price": 4.80},
    {"code": "ADA715", "name": "Adafruit I2C Controlled + Keypad Shield Kit for 16x2 LCD", "qty": 1, "price": 3.10},
    {"code": "ADA3135", "name": "Adafruit 15x7 CharliePlex LED Matrix Display FeatherWing - Yellow", "qty": 1, "price": 2.25},
    {"code": "PIM321", "name": "pHAT Stack - Solder Yourself Kit", "qty": 1, "price": 2.95},
    {"code": "PIM549", "name": "Pico Breakout Garden Base", "qty": 1, "price": 11.00},
    {"code": "PIM569", "name": "MICS6814 3-in-1 Gas Sensor Breakout (CO, NO2, NH3)", "qty": 1, "price": 19.25},
    {"code": "PIM461", "name": "Fan SHIM for Raspberry Pi", "qty": 1, "price": 10.00},
    {"code": "PIM527", "name": "LED Dot Matrix Breakout - Green", "qty": 1, "price": 3.55},
    {"code": "PIM409", "name": "I2C Breakout Extender (pack of 3)", "qty": 1, "price": 1.90},
    {"code": "IFIX-EU145439-1", "name": "Mahi 1/4\" Bit Driver", "qty": 1, "price": 4.60},
    {"code": "PIM333", "name": "Scroll pHAT HD - Yellow", "qty": 1, "price": 3.45},
    {"code": "PIM587", "name": "SCD41 CO2 Sensor Breakout (Carbon Dioxide / Temperature / Humidity)", "qty": 1, "price": 45.50},
    {"code": "PIM447", "name": "Trackball Breakout", "qty": 1, "price": 12.75},
    {"code": "WPM463", "name": "2 Channel Solid State Relay Module", "qty": 1, "price": 3.30},
    {"code": "POL-5065", "name": "Motoron Dual Motor Controller - M2T256 - I2C", "qty": 1, "price": 6.90},
    {"code": "POL-2122", "name": "Pololu 3.3V Step-Up/Step-Down Voltage Regulator S7V8F3", "qty": 1, "price": 4.60},
]

PRODUCT_DATA = {
    "PIM373": {
        "description": "VL53L1X Time of Flight sensor breakout from Pimoroni. Measures distances up to 4m using a laser. I2C interface with Breakout Garden compatible header.",
        "specifications": "Sensor: VL53L1X; Range: 40mm-4000mm; Interface: I2C (0x29); Voltage: 3.3V; Laser: 940nm Class 1 VCSEL; FoV: 27°; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-vl53l1x-breakout",
        "category": "Sensor",
        "page_url": "https://shop.pimoroni.com/products/vl53l1x-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM373-1_1024x1024.jpg"
    },
    "PIM301": {
        "description": "Button SHIM - a slim 5-button input add-on for Raspberry Pi. Uses only one GPIO pin with an interrupt-driven design.",
        "specifications": "Buttons: 5 (A, B, C, D, E); Interface: I2C; Form Factor: SHIM (slim HAT); LED: 1x RGB pixel; Compatible: All 40-pin Pi",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-button-shim",
        "category": "Breakout Board",
        "page_url": "https://shop.pimoroni.com/products/button-shim",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM301-1_1024x1024.jpg"
    },
    "PIM449": {
        "description": "RV3028 Real-Time Clock breakout from Pimoroni. Ultra-low power RTC with battery backup and Breakout Garden I2C header.",
        "specifications": "IC: RV3028; Accuracy: ±1 ppm; Interface: I2C (0x52); Battery: CR1220 backup; Current Draw: 40nA; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-rv3028-real-time-clock-breakout",
        "category": "Breakout Board",
        "page_url": "https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM449-1_1024x1024.jpg"
    },
    "PIM575": {
        "description": "BME688 4-in-1 air quality breakout. Measures gas (VOC), temperature, pressure, and humidity with AI gas scanning capabilities.",
        "specifications": "Sensor: BME688; Measures: Gas/VOC, Temperature (±1°C), Pressure (±0.6hPa), Humidity (±3%RH); Interface: I2C; Voltage: 3.3V; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-bme688-breakout",
        "category": "Sensor",
        "page_url": "https://shop.pimoroni.com/products/bme688-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM575-1_1024x1024.jpg"
    },
    "BOB-19389": {
        "description": "SparkFun analog MEMS microphone breakout using the SPH8878LR5H-1. Outputs an analog signal proportional to sound.",
        "specifications": "Sensor: SPH8878LR5H-1; Type: Analog MEMS microphone; Frequency: 100Hz-10kHz; SNR: 65dB; Voltage: 3.3V; Output: Analog",
        "learn_guide_url": "https://learn.sparkfun.com/tutorials/analog-mems-microphone-breakout---sph8878lr5h-1-hookup-guide",
        "category": "Sensor",
        "page_url": "https://www.sparkfun.com/products/19389",
        "image_url": "https://cdn.sparkfun.com/assets/parts/1/9/0/0/0/19389-SparkFun_Analog_MEMS_Microphone_Breakout_-_SPH8878LR5H-1-01.jpg"
    },
    "COM0216": {
        "description": "Single channel optoisolator / optocoupler. Electrically isolates two parts of a circuit using an LED and phototransistor.",
        "specifications": "Channels: 1; Type: Optocoupler; Isolation: Optical; Package: DIP-4",
        "learn_guide_url": None,
        "category": "Component",
        "page_url": "https://shop.pimoroni.com/products/optoisolator",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/COM0216-1_1024x1024.jpg"
    },
    "PA-21": {
        "description": "Engineer PA-21 universal crimping pliers. Precision Japanese-made crimping tool for various connector types.",
        "specifications": "Brand: Engineer; Model: PA-21; Type: Universal crimping pliers; Material: Carbon steel; Made in Japan",
        "learn_guide_url": None,
        "category": "Tool",
        "page_url": "https://shop.pimoroni.com/products/engineer-universal-crimping-pliers",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PA-21-1_1024x1024.jpg"
    },
    "COM0005": {
        "description": "Pico stacking header pack. Allows stacking add-on boards onto a Raspberry Pi Pico.",
        "specifications": "Pins: 2x 20-pin; Type: Female stacking headers; Pitch: 2.54mm; Compatible: Raspberry Pi Pico/Pico W",
        "learn_guide_url": None,
        "category": "Accessory",
        "page_url": "https://shop.pimoroni.com/products/pico-stacking-header-pack",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/COM0005-1_1024x1024.jpg"
    },
    "COM1117": {
        "description": "Pico header pack. Standard male headers for soldering onto a Raspberry Pi Pico.",
        "specifications": "Pins: 2x 20-pin; Type: Male headers; Pitch: 2.54mm; Compatible: Raspberry Pi Pico/Pico W",
        "learn_guide_url": None,
        "category": "Accessory",
        "page_url": "https://shop.pimoroni.com/products/pico-header-pack",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/COM1117-1_1024x1024.jpg"
    },
    "ADA1207": {
        "description": "Adafruit SMT breakout PCB for SOIC or TSSOP packages, 16-pin, pack of three. Adapts surface-mount ICs to breadboard-friendly DIP.",
        "specifications": "Quantity: 3; Pins: 16; Compatible: SOIC and TSSOP packages; Output: DIP breadboard spacing",
        "learn_guide_url": None,
        "category": "Prototyping",
        "page_url": "https://www.adafruit.com/product/1207",
        "image_url": "https://cdn-shop.adafruit.com/970x728/1207-00.jpg"
    },
    "ADA1211": {
        "description": "Adafruit SMT breakout PCB for SOIC or TSSOP packages, 12-pin, pack of six. Adapts surface-mount ICs to breadboard-friendly DIP.",
        "specifications": "Quantity: 6; Pins: 12; Compatible: SOIC and TSSOP packages; Output: DIP breadboard spacing",
        "learn_guide_url": None,
        "category": "Prototyping",
        "page_url": "https://www.adafruit.com/product/1211",
        "image_url": "https://cdn-shop.adafruit.com/970x728/1211-00.jpg"
    },
    "PIM479": {
        "description": "DRV8830 DC motor driver breakout from Pimoroni. I2C-controlled motor driver for small DC motors with Breakout Garden header.",
        "specifications": "IC: DRV8830; Interface: I2C (0x60-0x63); Voltage: 2.75-6.8V motor; Current: 1A peak; Features: Speed + direction; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-drv8830-motor-driver-breakout",
        "category": "Breakout Board",
        "page_url": "https://shop.pimoroni.com/products/drv8830-dc-motor-driver-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM479-1_1024x1024.jpg"
    },
    "PIM442": {
        "description": "11x7 LED matrix breakout from Pimoroni. I2C-controlled white LED matrix with individual brightness control per pixel.",
        "specifications": "Matrix: 11x7 (77 LEDs); Color: White; Driver: IS31FL3731; Interface: I2C; Brightness: 8-bit per pixel; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-11x7-led-matrix-breakout",
        "category": "Display",
        "page_url": "https://shop.pimoroni.com/products/11x7-led-matrix-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM442-1_1024x1024.jpg"
    },
    "PIM435": {
        "description": "5x5 RGB LED matrix breakout from Pimoroni. 25 individually-addressable RGB LEDs driven over I2C with Breakout Garden header.",
        "specifications": "Matrix: 5x5 (25 LEDs); Color: RGB; Driver: IS31FL3731; Interface: I2C; Brightness: 8-bit per channel; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-5x5-rgb-matrix-breakout",
        "category": "Display",
        "page_url": "https://shop.pimoroni.com/products/5x5-rgb-matrix-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM435-1_1024x1024.jpg"
    },
    "PIM517": {
        "description": "IO Expander breakout from Pimoroni. Adds 14 multi-function I/O pins controllable via I2C including PWM, ADC, and digital I/O.",
        "specifications": "IC: Nuvoton MS51; GPIO: 14 (6x ADC, 6x PWM capable); Interface: I2C; Voltage: 3.3V; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-io-expander-breakout",
        "category": "Breakout Board",
        "page_url": "https://shop.pimoroni.com/products/io-expander",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM517-1_1024x1024.jpg"
    },
    "PIM438": {
        "description": "MAX30101 breakout for heart rate, blood oxygen (SpO2), and smoke detection. High-sensitivity optical sensor with I2C interface.",
        "specifications": "Sensor: MAX30101; Measures: Heart rate, SpO2, smoke/particles; LEDs: Red + IR + Green; Interface: I2C (0x57); Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-max30101-breakout",
        "category": "Sensor",
        "page_url": "https://shop.pimoroni.com/products/max30101-breakout-heart-rate-oximeter-smoke-sensor",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM438-1_1024x1024.jpg"
    },
    "COM3900": {
        "description": "Breakout Garden I2C connector headers, pack of 5. Standard 5-pin I2C headers used by Pimoroni Breakout Garden ecosystem.",
        "specifications": "Quantity: 5; Pins: 5 (3V3, SDA, SCL, INT, GND); Pitch: 2.54mm; Ecosystem: Breakout Garden",
        "learn_guide_url": None,
        "category": "Cable/Connector",
        "page_url": "https://shop.pimoroni.com/products/breakout-garden-i2c-connector-pack-of-5",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/COM3900-1_1024x1024.jpg"
    },
    "PIM572": {
        "description": "Breakout Garden to STEMMA QT / Qwiic adapter. Converts Pimoroni Breakout Garden I2C header to JST SH 4-pin STEMMA QT / Qwiic.",
        "specifications": "Input: Breakout Garden 5-pin; Output: STEMMA QT / Qwiic JST SH 4-pin; Type: Adapter PCB",
        "learn_guide_url": None,
        "category": "Cable/Connector",
        "page_url": "https://shop.pimoroni.com/products/breakout-garden-to-stemma-qt-qwiic-adapter",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM572-1_1024x1024.jpg"
    },
    "PIM455": {
        "description": "HT0740 40V/10A switch breakout from Pimoroni. I2C-controlled high-side power switch for switching high-voltage/current loads.",
        "specifications": "IC: HT0740; Voltage: Up to 40V; Current: Up to 10A; Interface: I2C (0x38-0x3F); Type: High-side N-FET switch; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-ht0740-breakout",
        "category": "Breakout Board",
        "page_url": "https://shop.pimoroni.com/products/ht0740-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM455-1_1024x1024.jpg"
    },
    "ADA5664": {
        "description": "Adafruit PCA9546 4-channel STEMMA QT / Qwiic I2C multiplexer. TCA9546A compatible, allows 4 separate I2C buses from one port.",
        "specifications": "IC: PCA9546; Channels: 4; Interface: I2C; Voltage: 3.3-5V; Connector: STEMMA QT / Qwiic; Compatible: TCA9546A",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-pca9546-4-channel-i2c-multiplexer",
        "category": "Breakout Board",
        "page_url": "https://www.adafruit.com/product/5664",
        "image_url": "https://cdn-shop.adafruit.com/970x728/5664-00.jpg"
    },
    "PIM699": {
        "description": "NVMe Base for Raspberry Pi 5. Adds M.2 NVMe SSD storage to the Pi 5 via the PCIe connector on the bottom of the board.",
        "specifications": "Interface: M.2 M-Key (2230/2242); Connection: PCIe Gen 2 x1 via FPC; Compatible: Raspberry Pi 5; Speed: Up to ~800MB/s",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-nvme-base",
        "category": "Accessory",
        "page_url": "https://shop.pimoroni.com/products/nvme-base",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM699-1_1024x1024.jpg"
    },
    "PIM560": {
        "description": "Pimoroni Pico LiPo - a RP2040 board with 16MB flash, LiPo/LiIon battery management, USB-C, and STEMMA QT / Qwiic connector.",
        "specifications": "MCU: RP2040 (Dual ARM Cortex M0+); Clock: 133MHz; Flash: 16MB QSPI; RAM: 264KB; USB: USB-C; Battery: LiPo/LiIon charger; Connector: STEMMA QT; GPIO: 22",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-pico-lipo",
        "category": "Microcontroller",
        "page_url": "https://shop.pimoroni.com/products/pimoroni-pico-lipo",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM560-1_1024x1024.jpg"
    },
    "POL-3781": {
        "description": "Pololu D36V28F3 step-down voltage regulator. Efficient 3.3V 3.6A buck converter with wide input range.",
        "specifications": "Output: 3.3V; Max Current: 3.6A; Input: 4.5-50V; Type: Step-down (buck); Efficiency: Up to 95%; Brand: Pololu",
        "learn_guide_url": None,
        "category": "Power",
        "page_url": "https://www.pololu.com/product/3781",
        "image_url": "https://a.pololu-files.com/picture/0J11774.1200.jpg"
    },
    "ADA4258": {
        "description": "Adafruit LPS35HW water-resistant pressure sensor with STEMMA QT. Measures barometric pressure with a gel-protected sensor element.",
        "specifications": "Sensor: LPS35HW; Range: 260-1260 hPa; Accuracy: ±0.1 hPa; Interface: I2C/SPI; Feature: Water-resistant gel coating; Connector: STEMMA QT",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-lps35hw-water-resistant-barometric-pressure-sensor",
        "category": "Sensor",
        "page_url": "https://www.adafruit.com/product/4258",
        "image_url": "https://cdn-shop.adafruit.com/970x728/4258-00.jpg"
    },
    "ADA715": {
        "description": "Adafruit I2C controlled keypad shield kit for 16x2 LCD. Same as Adafruit product 715, purchased via Pimoroni.",
        "specifications": "Display: 16x2 character LCD; Interface: I2C; Buttons: 5 (Select, Up, Down, Left, Right); Voltage: 5V; Shield: Arduino UNO compatible",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-i2c-controlled-keypad-shield-for-16x2-lcd",
        "category": "Display",
        "page_url": "https://www.adafruit.com/product/715",
        "image_url": "https://cdn-shop.adafruit.com/970x728/715-00.jpg"
    },
    "ADA3135": {
        "description": "Adafruit 15x7 CharliePlex LED matrix display FeatherWing in yellow. Same as Adafruit 3134 but yellow color.",
        "specifications": "Matrix: 15x7 (105 LEDs); Color: Yellow; Driver: IS31FL3731; Interface: I2C; Form Factor: FeatherWing",
        "learn_guide_url": "https://learn.adafruit.com/adafruit-15x7-7x15-charlieplex-led-matrix-display-featherwing",
        "category": "FeatherWing",
        "page_url": "https://www.adafruit.com/product/3135",
        "image_url": "https://cdn-shop.adafruit.com/970x728/3135-00.jpg"
    },
    "PIM321": {
        "description": "pHAT Stack solder-yourself kit. Lets you stack up to 5 Pimoroni pHATs or mini HATs on a single Raspberry Pi.",
        "specifications": "Slots: Up to 5 pHATs; Type: Stacking adapter; Assembly: Solder required; Compatible: All 40-pin Pi",
        "learn_guide_url": "https://learn.pimoroni.com/article/assembling-phat-stack",
        "category": "Accessory",
        "page_url": "https://shop.pimoroni.com/products/phat-stack",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM321-1_1024x1024.jpg"
    },
    "PIM549": {
        "description": "Pico Breakout Garden Base from Pimoroni. Adds two I2C and one SPI Breakout Garden slots to a Raspberry Pi Pico.",
        "specifications": "Slots: 2x I2C + 1x SPI Breakout Garden; Compatible: Raspberry Pi Pico/Pico W; Connector: STEMMA QT / Qwiic; Feature: Reset button",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-pico-breakout-garden",
        "category": "Accessory",
        "page_url": "https://shop.pimoroni.com/products/pico-breakout-garden-base",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM549-1_1024x1024.jpg"
    },
    "PIM569": {
        "description": "MICS6814 3-in-1 gas sensor breakout from Pimoroni. Detects carbon monoxide (CO), nitrogen dioxide (NO2), and ammonia (NH3).",
        "specifications": "Sensor: MICS6814; Gases: CO, NO2, NH3; Interface: I2C (via ADC); Voltage: 3.3V; Type: Analog MEMS; Heater: Built-in; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-mics6814-breakout",
        "category": "Sensor",
        "page_url": "https://shop.pimoroni.com/products/mics6814-gas-sensor-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM569-1_1024x1024.jpg"
    },
    "PIM461": {
        "description": "Fan SHIM for Raspberry Pi. Slim add-on with a 30mm fan and LED for active cooling, controllable via software.",
        "specifications": "Fan: 30mm; Control: GPIO (software PWM); LED: 1x RGB; Current: ~100mA; Form Factor: SHIM; Compatible: All 40-pin Pi",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-fan-shim",
        "category": "Accessory",
        "page_url": "https://shop.pimoroni.com/products/fan-shim",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM461-1_1024x1024.jpg"
    },
    "PIM527": {
        "description": "LED dot matrix breakout in green from Pimoroni. 5x7 green LED matrix driven over I2C via Breakout Garden header.",
        "specifications": "Matrix: 7x5 (35 LEDs); Color: Green; Driver: IS31FL3730; Interface: I2C; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-led-dot-matrix-breakout",
        "category": "Display",
        "page_url": "https://shop.pimoroni.com/products/led-dot-matrix-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM527-1_1024x1024.jpg"
    },
    "PIM409": {
        "description": "I2C breakout extender from Pimoroni, pack of 3. Extends Breakout Garden I2C headers with wire-friendly connections.",
        "specifications": "Quantity: 3; Type: I2C breakout extender; Pins: 5 (3V3, SDA, SCL, INT, GND); Ecosystem: Breakout Garden",
        "learn_guide_url": None,
        "category": "Cable/Connector",
        "page_url": "https://shop.pimoroni.com/products/i2c-breakout-extender-pack-of-3",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM409-1_1024x1024.jpg"
    },
    "IFIX-EU145439-1": {
        "description": "Mahi 1/4 inch bit driver from iFixit. Precision screwdriver with magnetic bit holder and comfortable grip.",
        "specifications": "Bit Size: 1/4\" (6.35mm); Type: Magnetic bit driver; Brand: iFixit/Mahi; Feature: Swivel top cap",
        "learn_guide_url": None,
        "category": "Tool",
        "page_url": "https://www.ifixit.com/products/mahi-driver",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/IFIX-EU145439-1-1_1024x1024.jpg"
    },
    "PIM333": {
        "description": "Scroll pHAT HD in yellow from Pimoroni. 17x7 LED matrix HAT for Raspberry Pi with scrolling text and graphics.",
        "specifications": "Matrix: 17x7 (119 LEDs); Color: Yellow; Driver: IS31FL3731; Interface: I2C; Form Factor: pHAT; Compatible: All 40-pin Pi",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-scroll-phat-hd",
        "category": "Display",
        "page_url": "https://shop.pimoroni.com/products/scroll-phat-hd",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM333-1_1024x1024.jpg"
    },
    "PIM587": {
        "description": "SCD41 CO2 sensor breakout from Pimoroni. Measures true CO2 concentration using photoacoustic sensing, plus temperature and humidity.",
        "specifications": "Sensor: SCD41; CO2 Range: 400-5000 ppm; CO2 Accuracy: ±(40ppm + 5%); Temperature: ±0.8°C; Humidity: ±6%RH; Interface: I2C; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-scd41-co2-breakout",
        "category": "Sensor",
        "page_url": "https://shop.pimoroni.com/products/scd41-co2-sensor-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM587-1_1024x1024.jpg"
    },
    "PIM447": {
        "description": "Trackball breakout from Pimoroni. A mini trackball with RGBW LED backlight, controllable over I2C via Breakout Garden header.",
        "specifications": "Type: Trackball (5-way: up/down/left/right/click); LED: RGBW backlight; Interface: I2C (0x0A); Interrupt: Yes; Connector: Breakout Garden",
        "learn_guide_url": "https://learn.pimoroni.com/article/getting-started-with-trackball-breakout",
        "category": "Breakout Board",
        "page_url": "https://shop.pimoroni.com/products/trackball-breakout",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/PIM447-1_1024x1024.jpg"
    },
    "WPM463": {
        "description": "2-channel solid state relay module. Safely switches AC or DC loads using optically-isolated solid state relays.",
        "specifications": "Channels: 2; Type: Solid State Relay; Isolation: Optical; Trigger: 3.3-5V logic; Load: AC/DC",
        "learn_guide_url": None,
        "category": "Component",
        "page_url": "https://shop.pimoroni.com/products/2-channel-solid-state-relay-module",
        "image_url": "https://cdn.shopify.com/s/files/1/0174/1800/products/WPM463-1_1024x1024.jpg"
    },
    "POL-5065": {
        "description": "Pololu Motoron M2T256 dual motor controller with I2C interface. Controls two brushed DC motors with current limiting.",
        "specifications": "Motors: 2x brushed DC; Interface: I2C; Voltage: 6.5-48V motor; Current: 2A continuous per channel; PWM: 20kHz; Brand: Pololu",
        "learn_guide_url": None,
        "category": "Breakout Board",
        "page_url": "https://www.pololu.com/product/5065",
        "image_url": "https://a.pololu-files.com/picture/0J12034.1200.jpg"
    },
    "POL-2122": {
        "description": "Pololu S7V8F3 3.3V step-up/step-down voltage regulator. Maintains steady 3.3V output from inputs above or below 3.3V.",
        "specifications": "Output: 3.3V; Max Current: 1A; Input: 2.7-11.8V; Type: Buck-boost; Efficiency: Up to 90%; Size: 7.5mm x 9.7mm; Brand: Pololu",
        "learn_guide_url": None,
        "category": "Power",
        "page_url": "https://www.pololu.com/product/2122",
        "image_url": "https://a.pololu-files.com/picture/0J4337.1200.jpg"
    },
}


def main():
    json_path = SCRIPT_DIR / "products.json"

    with open(json_path, encoding="utf-8") as fh:
        products = json.load(fh)

    for item in PIMORONI_PRODUCTS:
        code = item["code"]
        extra = PRODUCT_DATA.get(code, {})

        products[f"pimoroni_{code}"] = {
            "product_id": code,
            "name": item["name"],
            "csv_name": item["name"],
            "description": extra.get("description", ""),
            "technical_specs": extra.get("specifications", ""),
            "category": extra.get("category", "Uncategorized"),
            "page_url": extra.get("page_url", f"https://shop.pimoroni.com/search?q={code}"),
            "image_url": extra.get("image_url", ""),
            "learn_guide_url": extra.get("learn_guide_url"),
            "unit_price": item["price"],
            "currency": "GBP",
            "total_qty": item["qty"],
            "orders": ["pimoroni"],
            "source": "pimoroni.com",
            "last_scraped": None,
        }

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(products, fh, indent=2, ensure_ascii=False)

    print(f"Added {len(PIMORONI_PRODUCTS)} Pimoroni products. Total: {len(products)} products.")


if __name__ == "__main__":
    main()
