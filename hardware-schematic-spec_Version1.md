# Hardware Schematic Specification

## 1. Project Name
Motorized Mixer Controller Board

## 2. Purpose
This document defines the schematic-level electrical architecture of the board, including:
- power system
- MCU pin mapping
- motorized fader drive
- OLED display structure
- LED drive chain
- PCB-related electrical constraints

This file is intended for:
- schematic design
- PCB layout
- firmware implementation
- future AI-assisted analysis

---

## 3. System Overview

The board is built around a Teensy 4.1 and controls:
- 5 motorized faders
- 5 OLED displays
- 25 WS2812B LEDs
- multiple input expansion devices

Power input is 12V DC and is converted locally into:
- 5V
- 3.3V
- 10V

### Voltage rail usage
- 12V: raw incoming power bus
- 10V: motor drive rail
- 5V: WS2812B supply and 3.3V regulator input
- 3.3V: MCU and logic rail

---

## 4. Main Components

### 4.1 MCU
- Teensy 4.1

### 4.2 Faders
- RSA0N11M9A0J × 5
- rated motor voltage: 10V DC
- motor max current: 800mA or less
- total potentiometer resistance: 10kΩ
- travel: 100mm

### 4.3 Motor Drivers
- TB6612 × 3

### 4.4 I2C Multiplexer
- TCA9548A × 1

### 4.5 Displays
- 0.96" I2C OLED × 5

### 4.6 LEDs
- WS2812B × 25

### 4.7 Power
- MP2315SGJ-Z × 2
- AMS1117-3.3 × 1

---

## 5. Power System

### 5.1 Input Stage
External input:
- 12V DC jack

DC jack pin mapping:
- Pin1 = +12V
- Pin2 = GND
- Pin3 = not used

Power switch:
- COM connected to DC jack Pin1
- NO connected to +12V switched bus

### 5.2 12V Main Bus
The switched 12V bus powers:
- MP2315 #1 for 5V generation
- MP2315 #2 for 10V generation

### 5.3 12V to 5V Buck
Converter:
- MP2315SGJ-Z

Connections:
- IN/VCC/EN to +12V
- GND/AAM to GND
- BST to SW through 100nF
- SW to output through 10uH inductor
- SS34 from SW to GND
- output capacitors:
  - 100uF
  - 100nF
- FB divider:
  - 100kΩ top
  - 20kΩ bottom

Output:
- approximately 4.8V

### 5.4 12V to 10V Buck
Converter:
- MP2315SGJ-Z

Connections:
- IN/VCC/EN to +12V
- GND/AAM to GND
- BST to SW through 100nF
- SW to output through 10uH / 5A inductor
- SS34 from SW to GND
- output capacitors:
  - 100uF
  - 100nF
- FB divider:
  - 100kΩ top
  - 8.2kΩ bottom

Output:
- approximately 10.56V

Use:
- motor drive rail only

### 5.5 5V to 3.3V LDO
Regulator:
- AMS1117-3.3

Connections:
- IN to 5V
- GND to GND
- OUT to 3.3V
- output capacitors:
  - 10uF
  - 100nF

---

## 6. MCU Pin Allocation

### 6.1 I2C
- Pin18 = I2C_SDA
- Pin19 = I2C_SCL

### 6.2 WS2812B
- Pin10 = LED data

### 6.3 Fader ADC
- Pin14 (A0) = Fader1 wiper
- Pin15 (A1) = Fader2 wiper
- Pin16 (A2) = Fader3 wiper
- Pin17 (A3) = Fader4 wiper
- Pin20 (A6) = Fader5 wiper

### 6.4 Motor Driver Control
#### Driver 1
- Pin23 = DRV1_PWMA
- Pin41 = DRV1_AIN1
- Pin40 = DRV1_AIN2
- Pin22 = DRV1_PWMB
- Pin38 = DRV1_BIN1
- Pin39 = DRV1_BIN2

#### Driver 2
- Pin21 = DRV2_PWMA
- Pin37 = DRV2_AIN1
- Pin36 = DRV2_AIN2
- Pin13 = DRV2_PWMB
- Pin35 = DRV2_BIN1
- Pin34 = DRV2_BIN2

#### Driver 3
- Pin31 = DRV3_PWMA
- Pin32 = DRV3_AIN1
- Pin33 = DRV3_AIN2

---

## 7. I2C Display System

### 7.1 TCA9548A
Power:
- VCC = 3.3V
- GND = GND
- RESET# = 3.3V

Address:
- A0 = GND
- A1 = GND
- A2 = GND
- I2C address = 0x70

Main bus:
- SDA = Teensy Pin18
- SCL = Teensy Pin19

Pull-ups:
- SDA = 4.7kΩ to 3.3V
- SCL = 4.7kΩ to 3.3V

### 7.2 OLED Channels
- Channel 0 → OLED1
- Channel 1 → OLED2
- Channel 2 → OLED3
- Channel 3 → OLED4
- Channel 4 → OLED5

Each OLED:
- VCC → 3.3V
- GND → GND
- SDA/SCL → channel outputs
- local 100nF decoupling capacitor

---

## 8. WS2812B LED System

### 8.1 Data
- Teensy Pin10 → 330Ω series resistor → LED1 DIN

### 8.2 Chain
- LED1 DOUT → LED2 DIN
- ...
- LED24 DOUT → LED25 DIN

### 8.3 Power
- all LED VCC → 5V
- all LED GND → GND

### 8.4 Decoupling
Recommended per 5 LEDs:
- 100uF between 5V and GND
- 100nF between 5V and GND

---

## 9. Motorized Fader System

### 9.1 TB6612 Power
For each TB6612:
- VM → 10V
- VCC → 3.3V
- GND → GND
- STBY → 3.3V

Local decoupling:
- VM:
  - 100uF
  - 100nF
- VCC:
  - 100nF

### 9.2 Channel Assignment
- TB6612_1A → Fader1 motor
- TB6612_1B → Fader2 motor
- TB6612_2A → Fader3 motor
- TB6612_2B → Fader4 motor
- TB6612_3A → Fader5 motor

### 9.3 Fader 1
Motor:
- PWMA ← Pin23
- AIN1 ← Pin41
- AIN2 ← Pin40
- AO1/AO2 → motor terminals

Potentiometer:
- high end → 3.3V
- low end → GND
- wiper → Pin14(A0)

### 9.4 Fader 2
Motor:
- PWMB ← Pin22
- BIN1 ← Pin38
- BIN2 ← Pin39
- BO1/BO2 → motor terminals

Potentiometer:
- high end → 3.3V
- low end → GND
- wiper → Pin15(A1)

### 9.5 Fader 3
Motor:
- PWMA ← Pin21
- AIN1 ← Pin37
- AIN2 ← Pin36
- AO1/AO2 → motor terminals

Potentiometer:
- high end → 3.3V
- low end → GND
- wiper → Pin16(A2)

### 9.6 Fader 4
Motor:
- PWMB ← Pin13
- BIN1 ← Pin35
- BIN2 ← Pin34
- BO1/BO2 → motor terminals

Potentiometer:
- high end → 3.3V
- low end → GND
- wiper → Pin17(A3)

### 9.7 Fader 5
Motor:
- PWMA ← Pin31
- AIN1 ← Pin32
- AIN2 ← Pin33
- AO1/AO2 → motor terminals

Potentiometer:
- high end → 3.3V
- low end → GND
- wiper → Pin20(A6)

---

## 10. PCB Electrical Design Guidance

### 10.1 High-current nets
Use wide traces for:
- 12V
- 10V motor rail
- 5V LED rail
- TB6612 motor outputs

### 10.2 Sensitive nets
Keep away from switching and motor noise:
- ADC lines
- I2C lines
- FB resistor divider traces

### 10.3 MP2315 layout priority
Critical nodes:
- SW
- BST capacitor loop
- input bypass loop
- output capacitor loop

### 10.4 Grounding
- use large continuous ground plane
- keep return paths short
- avoid mixing motor return currents into analog sensing area

---

## 11. Notes
1. Do not power fader motors directly from 12V.
2. 5V motor drive is not recommended for normal behavior.
3. MT3608 is not suitable for 12V to 10V conversion.
4. OLED address collision is solved by TCA9548A.
5. ADC sensing is designed around a 3.3V reference range.

---

## 12. Suggested Companion Documents
- docs/pinout.md
- docs/power-tree.md
- docs/pcb-layout-guide.md
- docs/fader-control.md
- docs/bringup-checklist.md