# Hardware Architecture Specification

## 1. Project Overview

This project is a Teensy 4.1 based motorized fader control board intended for later firmware development, schematic capture, PCB layout, and AI-assisted analysis.

The board includes:

- Teensy 4.1 as the main MCU
- 5 motorized faders
- 3 TB6612 motor driver ICs
- 5 I2C OLED displays
- 1 TCA9548A I2C multiplexer
- 25 WS2812B RGB indicator LEDs
- 2 HC4067 expansion multiplexers
- External 12V DC power input
- On-board power conversion for:
  - 12V → 5V
  - 5V → 3.3V
  - 12V → 10V

This document is intended to be used by:
- firmware developers
- schematic/PCB designers
- future maintainers
- other AI models for reasoning and code generation

---

## 2. System Functional Blocks

### 2.1 MCU
Main controller:
- Teensy 4.1

Responsibilities:
- read fader positions
- control TB6612 motor drivers
- control WS2812B LEDs
- communicate with OLED displays through TCA9548A
- scan or read extended input devices

---

### 2.2 Motorized Faders
Part number:
- RSA0N11M9A0J

Key parameters:
- travel: 100 mm
- total resistance: 10 kΩ
- motor rated voltage: 10V DC
- motor max current: 800mA or less

Each fader contains:
1. a DC motor for moving the slider
2. a potentiometer for detecting slider position

Design rule:
- motor section is driven by TB6612
- potentiometer section is read by Teensy ADC

---

### 2.3 Motor Drivers
Part:
- TB6612 × 3

Each TB6612 contains 2 H-bridge channels:
- A channel
- B channel

Total available channels:
- 6 channels

Used channels:
- 5 channels for 5 faders

Unused:
- 1 spare channel

---

### 2.4 OLED Display Subsystem
Displays:
- 5 × 0.96-inch I2C OLED
- typical driver family: SSD1306
- typical address: 0x3C

Because the displays likely share the same I2C address, they cannot be connected directly in parallel.
A TCA9548A I2C multiplexer is used to isolate them by channel.

---

### 2.5 I2C Multiplexer
Part:
- TCA9548A

Purpose:
- route the MCU I2C bus to one OLED channel at a time

Address configuration:
- A0 = GND
- A1 = GND
- A2 = GND
- address = 0x70

---

### 2.6 RGB Indicator LEDs
Part:
- WS2812B × 25

Purpose:
- status indication
- button indication
- state feedback

Power:
- 5V

Control:
- single-wire data from Teensy

---

### 2.7 Power System
External input:
- 12V DC

Derived rails:
- 5V rail
- 3.3V rail
- 10V rail

Rail usage:
- 12V: raw input bus only
- 10V: motor driver VM supply
- 5V: WS2812B and 3.3V regulator input
- 3.3V: logic, MCU, displays, multiplexers

---

## 3. Power Architecture

### 3.1 Input Power
External DC input:
- 12V DC

DC jack:
- Pin1 = +12V
- Pin2 = GND
- Pin3 = switch/detect, not used

Power switch:
- SPST rocker switch
- COM connected to DC jack Pin1
- NO output connected to 12V main bus

Power flow:
- 12V input → power switch → 12V main bus

---

### 3.2 12V Main Bus
The 12V main bus feeds:
- MP2315 #1 for 12V→5V
- MP2315 #2 for 12V→10V

No logic device should be powered directly from 12V.

---

### 3.3 12V → 5V Conversion
Converter:
- MP2315SGJ-Z

Purpose:
- supply WS2812B
- supply input of AMS1117-3.3

Basic implementation:
- IN/VCC/EN connected to 12V
- GND/AAM connected to GND
- BST connected to SW through 100nF capacitor
- SW connected to output through 10uH inductor
- Schottky diode from SW to GND
- output filtered by 100uF and 100nF
- FB divider:
  - R1 = 100kΩ
  - R2 = 20kΩ

Approximate output:
- about 4.8V

This is acceptable for:
- WS2812B
- AMS1117 input

---

### 3.4 5V → 3.3V Conversion
Regulator:
- AMS1117-3.3

Purpose:
- supply logic rail

Basic implementation:
- IN = 5V
- GND = GND
- OUT = 3.3V
- output capacitors:
  - 10uF
  - 100nF

3.3V rail powers:
- Teensy 4.1
- TCA9548A
- OLED displays
- HC4067
- TB6612 logic VCC

---

### 3.5 12V → 10V Conversion
Converter:
- MP2315SGJ-Z

Purpose:
- supply TB6612 VM rail for motor power

Basic implementation:
- IN/VCC/EN connected to 12V
- GND/AAM connected to GND
- BST connected to SW through 100nF capacitor
- SW connected to output through 10uH / 5A inductor
- Schottky diode from SW to GND
- output filtered by 100uF and 100nF
- FB divider:
  - R1 = 100kΩ
  - R2 = 8.2kΩ

Approximate output:
- about 10.56V

Rationale:
- fader motor rated voltage is 10V
- this rail is intended for motor drive only

---

## 4. MP2315 Pin Mapping Used in This Project

Symbol pin mapping used in the current schematic symbol:

- Pin1 = AAM
- Pin2 = IN
- Pin3 = SW
- Pin4 = GND
- Pin5 = BST
- Pin6 = EN
- Pin7 = VCC
- Pin8 = FB

### 4.1 12V→5V MP2315 wiring
- Pin2(IN) → 12V
- Pin7(VCC) → 12V
- Pin6(EN) → 12V
- Pin4(GND) → GND
- Pin1(AAM) → GND
- Pin5(BST) --100nF--> Pin3(SW)
- Pin3(SW) --10uH--> 5V output node
- SW --SS34--> GND
- 5V node --100uF--> GND
- 5V node --100nF--> GND
- 5V node --100kΩ--> Pin8(FB) --20kΩ--> GND

### 4.2 12V→10V MP2315 wiring
- Pin2(IN) → 12V
- Pin7(VCC) → 12V
- Pin6(EN) → 12V
- Pin4(GND) → GND
- Pin1(AAM) → GND
- Pin5(BST) --100nF--> Pin3(SW)
- Pin3(SW) --10uH/5A--> 10V output node
- SW --SS34--> GND
- 10V node --100uF--> GND
- 10V node --100nF--> GND
- 10V node --100kΩ--> Pin8(FB) --8.2kΩ--> GND

---

## 5. Motor Driver Architecture

### 5.1 TB6612 Power Connections
Each TB6612:
- VM → 10V rail
- VCC → 3.3V rail
- GND → GND
- STBY → 3.3V (default always enabled)

Recommended local decoupling per TB6612:
- VM:
  - 100uF to GND
  - 100nF to GND
- VCC:
  - 100nF to GND

---

### 5.2 Fader-to-TB6612 Channel Mapping

#### TB6612_1
- A channel → Fader 1 motor
- B channel → Fader 2 motor

#### TB6612_2
- A channel → Fader 3 motor
- B channel → Fader 4 motor

#### TB6612_3
- A channel → Fader 5 motor
- B channel → spare

---

### 5.3 Control Pin Allocation

#### TB6612_1
- PWMA ← Teensy Pin23
- AIN1 ← Teensy Pin41
- AIN2 ← Teensy Pin40
- AO1  → Fader1 Motor terminal A
- AO2  → Fader1 Motor terminal B

- PWMB ← Teensy Pin22
- BIN1 ← Teensy Pin38
- BIN2 ← Teensy Pin39
- BO1  → Fader2 Motor terminal A
- BO2  → Fader2 Motor terminal B

#### TB6612_2
- PWMA ← Teensy Pin21
- AIN1 ← Teensy Pin37
- AIN2 ← Teensy Pin36
- AO1  → Fader3 Motor terminal A
- AO2  → Fader3 Motor terminal B

- PWMB ← Teensy Pin13
- BIN1 ← Teensy Pin35
- BIN2 ← Teensy Pin34
- BO1  → Fader4 Motor terminal A
- BO2  → Fader4 Motor terminal B

#### TB6612_3
- PWMA ← Teensy Pin31
- AIN1 ← Teensy Pin32
- AIN2 ← Teensy Pin33
- AO1  → Fader5 Motor terminal A
- AO2  → Fader5 Motor terminal B

Unused:
- TB6612_3 B channel reserved

---

### 5.4 Motor Direction Logic
Per channel:
- forward:
  - IN1 = 1
  - IN2 = 0
  - PWM = duty control
- reverse:
  - IN1 = 0
  - IN2 = 1
  - PWM = duty control
- brake:
  - IN1 = 1
  - IN2 = 1
- stop/coast:
  - IN1 = 0
  - IN2 = 0

If actual motor movement direction is reversed:
- swap motor wires
or
- invert software direction logic

---

## 6. Fader Position Sensing

Each motorized fader includes a potentiometer section.

Recommended analog connection:
- potentiometer high end → 3.3V
- potentiometer low end → GND
- potentiometer wiper → Teensy ADC input

This keeps ADC range safely within:
- 0V to 3.3V

### ADC allocation
- Fader1 wiper → Pin14 (A0)
- Fader2 wiper → Pin15 (A1)
- Fader3 wiper → Pin16 (A2)
- Fader4 wiper → Pin17 (A3)
- Fader5 wiper → Pin20 (A6)

Optional filtering per wiper:
- 100Ω series resistor
- 100nF capacitor from ADC node to GND

Purpose:
- reduce motor noise and ADC jitter

---

## 7. I2C Display Architecture

### 7.1 Teensy to TCA9548A
- Teensy Pin18 → SDA
- Teensy Pin19 → SCL

TCA9548A:
- VCC → 3.3V
- GND → GND
- RESET# → 3.3V
- A0 → GND
- A1 → GND
- A2 → GND
- address = 0x70

Host I2C pull-ups:
- SDA → 4.7kΩ → 3.3V
- SCL → 4.7kΩ → 3.3V

### 7.2 OLED channel mapping
- channel 0 → OLED_1
- channel 1 → OLED_2
- channel 2 → OLED_3
- channel 3 → OLED_4
- channel 4 → OLED_5

Each OLED:
- VCC → 3.3V
- GND → GND
- SDA/SCL → corresponding TCA channel lines

Recommended decoupling per OLED:
- 100nF between VCC and GND

---

## 8. WS2812B Architecture

### 8.1 Control
- Teensy Pin10 → 330Ω resistor → LED1 DIN

### 8.2 Daisy chain
- LED1 DOUT → LED2 DIN
- LED2 DOUT → LED3 DIN
- ...
- LED24 DOUT → LED25 DIN

### 8.3 Power
All WS2812B:
- VCC → 5V
- GND → GND

### 8.4 Decoupling
Recommended every 5 LEDs:
- 100uF between 5V and GND
- 100nF between 5V and GND

Important:
These capacitors are in parallel, not series.

Correct form:
- 5V ──┬──100uF──GND
-      └──100nF──GND

---

## 9. Known Confirmed Capacitor Parts

### 9.1 Large capacitor
- HGC1206R5107M100NSPJ
- interpreted as:
  - 100uF
  - 10V
  - 1206
- acceptable for filtering use

### 9.2 Small capacitor
- CGA0603X7R104K500JT
- interpreted as:
  - 100nF
  - 50V
  - X7R
  - 0603
- acceptable for decoupling and filtering use

---

## 10. Current Confirmed Teensy Pin Usage

Confirmed from prior design discussion:
- Pin10 → WS2812B data
- Pin18 → I2C SDA
- Pin19 → I2C SCL

TB6612 control:
- Pin13 → TB6612_2 PWMB
- Pin21 → TB6612_2 PWMA
- Pin22 → TB6612_1 PWMB
- Pin23 → TB6612_1 PWMA
- Pin31 → TB6612_3 PWMA
- Pin32 → TB6612_3 AIN1
- Pin33 → TB6612_3 AIN2
- Pin34 → TB6612_2 BIN2
- Pin35 → TB6612_2 BIN1
- Pin36 → TB6612_2 AIN2
- Pin37 → TB6612_2 AIN1
- Pin38 → TB6612_1 BIN1
- Pin39 → TB6612_1 BIN2
- Pin40 → TB6612_1 AIN2
- Pin41 → TB6612_1 AIN1

Fader ADC:
- Pin14 (A0) → Fader1 wiper
- Pin15 (A1) → Fader2 wiper
- Pin16 (A2) → Fader3 wiper
- Pin17 (A3) → Fader4 wiper
- Pin20 (A6) → Fader5 wiper

---

## 11. Design Constraints and Notes

1. Fader motor rated voltage is 10V, so do not drive motor directly from 12V.
2. 5V is not recommended for the fader motor if normal motorized behavior is required.
3. MT3608 cannot be used for 12V→10V because it is a boost converter, not a buck converter.
4. OLED address conflict is resolved through TCA9548A.
5. TB6612 STBY is currently planned as tied high to 3.3V for simplicity.
6. Unused TB6612 inputs should not float.
7. ADC lines for faders should be routed away from motor switching nodes.
8. MP2315 SW nodes must be short and isolated from sensitive analog/I2C traces.
9. High-current rails should use wide traces and solid ground return.

---

## 12. Suggested Future Documentation
Recommended future repository documents:
- docs/hardware-architecture.md
- docs/pinout.md
- docs/power-tree.md
- docs/fader-control.md
- docs/bringup-checklist.md

---

## 13. Suggested Next Tasks
1. finalize TB6612 spare channel handling
2. finalize HC4067 signal mapping
3. create complete BOM
4. create pinout table document
5. create firmware abstraction layer around:
   - fader motor control
   - fader ADC readback
   - OLED channel selection
   - WS2812B state control