# Hardware Schematic Specification

## 1. Overview

This project is a Teensy 4.1 based motorized mixer controller board.

Main hardware modules:

- Teensy 4.1 main controller
- 5 motorized faders
- 3 TB6612 motor driver ICs
- 5 I2C OLED displays
- 1 TCA9548A I2C multiplexer
- 25 WS2812B RGB LEDs
- 2 HC4067 expansion multiplexers
- External 12V DC input
- On-board power conversion for:
  - 12V → 5V
  - 12V → 10V
  - 5V → 3.3V

This document is intended to support:
- schematic capture
- PCB layout
- firmware development
- hardware bring-up
- future AI-assisted understanding

---

## 2. System Architecture

### 2.1 Main rails
The board uses these power rails:

- `+12V_IN`: DC jack raw input
- `+12V_SW`: switched 12V main bus
- `+5V_LED`: 5V rail generated from 12V
- `+3V3_LOGIC`: 3.3V logic rail generated from 5V
- `+10V_MOTOR`: 10V rail generated from 12V for motor drive
- `GND`: common ground

### 2.2 Rail usage
- `+12V_SW` feeds buck converters only
- `+5V_LED` powers WS2812B and AMS1117 input
- `+3V3_LOGIC` powers logic and control devices
- `+10V_MOTOR` powers TB6612 VM and the fader motors

---

## 3. Main Components

### 3.1 MCU
- Teensy 4.1

### 3.2 Motorized faders
- Part number: RSA0N11M9A0J
- Quantity: 5
- Travel: 100 mm
- Potentiometer value: 10 kΩ
- Motor rated voltage: 10V DC
- Motor max current: 800mA or less

Each fader has:
1. a motor section
2. a potentiometer section

### 3.3 Motor driver ICs
- TB6612 × 3

Each TB6612 provides:
- 2 H-bridge channels
- A channel
- B channel

Used channels:
- 5 channels total for 5 faders

Unused:
- 1 spare channel

### 3.4 Displays
- 0.96-inch I2C OLED × 5
- Typical driver family: SSD1306
- Typical address: 0x3C

### 3.5 I2C multiplexer
- TCA9548A × 1

Purpose:
- avoid OLED I2C address conflict

### 3.6 RGB LEDs
- WS2812B × 25

### 3.7 Power devices
- MP2315SGJ-Z × 2
- AMS1117-3.3 × 1

---

## 4. Input Power Stage

### 4.1 DC jack
Recommended type:
- DC-005-5A-2.5 or equivalent

Pin definition:
- Pin1 = +12V
- Pin2 = GND
- Pin3 = detect/switch pin, not used

### 4.2 Power switch
SPST rocker switch:
- COM connected to DC jack Pin1
- NO connected to `+12V_SW`

Power path:
- `DC_JACK.Pin1 → SW_POWER.COM`
- `SW_POWER.NO → +12V_SW`
- `DC_JACK.Pin2 → GND`

---

## 5. 12V to 5V Converter

### 5.1 Device
- MP2315SGJ-Z

### 5.2 Symbol pin mapping used in this project
- Pin1 = AAM
- Pin2 = IN
- Pin3 = SW
- Pin4 = GND
- Pin5 = BST
- Pin6 = EN
- Pin7 = VCC
- Pin8 = FB

### 5.3 Connections
- `Pin2(IN) → +12V_SW`
- `Pin7(VCC) → +12V_SW`
- `Pin6(EN) → +12V_SW`
- `Pin4(GND) → GND`
- `Pin1(AAM) → GND`
- `Pin5(BST) --100nF--> Pin3(SW)`
- `Pin3(SW) --10uH--> +5V_LED`
- `SW --SS34--> GND`
- `+12V_SW --10uF--> GND`
- `+5V_LED --100uF--> GND`
- `+5V_LED --100nF--> GND`

### 5.4 Feedback divider
- `+5V_LED → 100kΩ → FB`
- `FB → 20kΩ → GND`

Estimated output:
- about 4.8V

Use:
- WS2812B supply
- AMS1117 input

---

## 6. 12V to 10V Converter

### 6.1 Device
- MP2315SGJ-Z

### 6.2 Connections
- `Pin2(IN) → +12V_SW`
- `Pin7(VCC) → +12V_SW`
- `Pin6(EN) → +12V_SW`
- `Pin4(GND) → GND`
- `Pin1(AAM) → GND`
- `Pin5(BST) --100nF--> Pin3(SW)`
- `Pin3(SW) --10uH/5A--> +10V_MOTOR`
- `SW --SS34--> GND`
- `+12V_SW --10uF--> GND`
- `+10V_MOTOR --100uF--> GND`
- `+10V_MOTOR --100nF--> GND`

### 6.3 Feedback divider
- `+10V_MOTOR → 100kΩ → FB`
- `FB → 8.2kΩ → GND`

Estimated output:
- about 10.56V

Use:
- TB6612 VM
- fader motor supply only

---

## 7. 5V to 3.3V Regulator

### 7.1 Device
- AMS1117-3.3

### 7.2 Connections
- `IN → +5V_LED`
- `GND → GND`
- `OUT → +3V3_LOGIC`

### 7.3 Capacitors
- `IN --10uF--> GND`
- `OUT --10uF--> GND`
- `OUT --100nF--> GND`

Use:
- logic rail generation

---

## 8. Teensy 4.1 Pin Mapping

### 8.1 I2C
- `Pin18 → I2C_SDA`
- `Pin19 → I2C_SCL`

### 8.2 WS2812B
- `Pin10 → LED_DATA`

### 8.3 Fader ADC inputs
- `Pin14(A0) → FADER1_ADC`
- `Pin15(A1) → FADER2_ADC`
- `Pin16(A2) → FADER3_ADC`
- `Pin17(A3) → FADER4_ADC`
- `Pin20(A6) → FADER5_ADC`

### 8.4 Motor driver control
#### TB6612_1
- `Pin23 → DRV1_PWMA`
- `Pin41 → DRV1_AIN1`
- `Pin40 → DRV1_AIN2`
- `Pin22 → DRV1_PWMB`
- `Pin38 → DRV1_BIN1`
- `Pin39 → DRV1_BIN2`

#### TB6612_2
- `Pin21 → DRV2_PWMA`
- `Pin37 → DRV2_AIN1`
- `Pin36 → DRV2_AIN2`
- `Pin13 → DRV2_PWMB`
- `Pin35 → DRV2_BIN1`
- `Pin34 → DRV2_BIN2`

#### TB6612_3
- `Pin31 → DRV3_PWMA`
- `Pin32 → DRV3_AIN1`
- `Pin33 → DRV3_AIN2`

---

## 9. TCA9548A and OLED Subsystem

### 9.1 TCA9548A power and address
- `VCC → +3V3_LOGIC`
- `GND → GND`
- `RESET# → +3V3_LOGIC`
- `A0 → GND`
- `A1 → GND`
- `A2 → GND`

I2C address:
- `0x70`

### 9.2 Main I2C connections
- `SDA → I2C_SDA`
- `SCL → I2C_SCL`

### 9.3 Pull-ups
- `I2C_SDA → 4.7kΩ → +3V3_LOGIC`
- `I2C_SCL → 4.7kΩ → +3V3_LOGIC`

### 9.4 OLED channel mapping
- Channel 0 → OLED1
- Channel 1 → OLED2
- Channel 2 → OLED3
- Channel 3 → OLED4
- Channel 4 → OLED5

Each OLED:
- `VCC → +3V3_LOGIC`
- `GND → GND`
- `SDA/SCL → corresponding TCA9548A channel`
- local `100nF` decoupling capacitor

---

## 10. WS2812B Subsystem

### 10.1 Data chain
- `Teensy Pin10 → 330Ω → LED1 DIN`
- `LED1 DOUT → LED2 DIN`
- ...
- `LED24 DOUT → LED25 DIN`

### 10.2 Power
All LEDs:
- `VCC → +5V_LED`
- `GND → GND`

### 10.3 Decoupling
Recommended every 5 LEDs:
- `100uF` between `+5V_LED` and `GND`
- `100nF` between `+5V_LED` and `GND`

---

## 11. TB6612 Motor Driver Subsystem

### 11.1 Power
For each TB6612:
- `VM → +10V_MOTOR`
- `VCC → +3V3_LOGIC`
- `GND → GND`
- `STBY → +3V3_LOGIC`

### 11.2 Local decoupling
Per TB6612:
- `VM --100uF--> GND`
- `VM --100nF--> GND`
- `VCC --100nF--> GND`

### 11.3 Channel assignment
- `TB6612_1A → Fader1 motor`
- `TB6612_1B → Fader2 motor`
- `TB6612_2A → Fader3 motor`
- `TB6612_2B → Fader4 motor`
- `TB6612_3A → Fader5 motor`
- `TB6612_3B → spare`

---

## 12. Fader Wiring

### 12.1 Fader1
Motor:
- `AO1 → FADER1_MA`
- `AO2 → FADER1_MB`

Potentiometer:
- `High end → +3V3_LOGIC`
- `Low end → GND`
- `Wiper → FADER1_ADC`

### 12.2 Fader2
Motor:
- `BO1 → FADER2_MA`
- `BO2 → FADER2_MB`

Potentiometer:
- `High end → +3V3_LOGIC`
- `Low end → GND`
- `Wiper → FADER2_ADC`

### 12.3 Fader3
Motor:
- `AO1 → FADER3_MA`
- `AO2 → FADER3_MB`

Potentiometer:
- `High end → +3V3_LOGIC`
- `Low end → GND`
- `Wiper → FADER3_ADC`

### 12.4 Fader4
Motor:
- `BO1 → FADER4_MA`
- `BO2 → FADER4_MB`

Potentiometer:
- `High end → +3V3_LOGIC`
- `Low end → GND`
- `Wiper → FADER4_ADC`

### 12.5 Fader5
Motor:
- `AO1 → FADER5_MA`
- `AO2 → FADER5_MB`

Potentiometer:
- `High end → +3V3_LOGIC`
- `Low end → GND`
- `Wiper → FADER5_ADC`

---

## 13. Notes and Constraints

1. Do not power fader motors directly from 12V.
2. 5V motor drive is not recommended for proper motorized fader operation.
3. MT3608 is not suitable for 12V→10V conversion because it is a boost converter.
4. OLED address conflict is resolved through TCA9548A.
5. ADC sensing is designed around a 3.3V input range.
6. High-current switching nodes must be kept away from ADC and I2C traces.

---

## 14. Suggested Companion Docs
- `docs/pinout.md`
- `docs/pcb-layout-guide.md`
- `docs/fader-control.md`
- `docs/bringup-checklist.md`