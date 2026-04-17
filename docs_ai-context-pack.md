# AI Context Pack

## 1. Purpose

This file is a compact, AI-oriented summary of the hardware design context for the motorized mixer controller board.

It is intended for:
- LLM input context
- future AI-assisted schematic work
- AI-assisted firmware generation
- AI-assisted documentation updates
- quick hardware state transfer between sessions

This file intentionally summarizes the most important stable design decisions.

---

## 2. Project Summary

This project is a Teensy 4.1 based motorized mixer controller board with:
- 5 motorized faders
- 3 TB6612 motor drivers
- 5 I2C OLED displays
- 1 TCA9548A I2C multiplexer
- 25 WS2812B LEDs
- 2 HC4067 expansion devices
- external 12V DC power input

Main goals:
- drive motorized faders
- read fader positions
- display channel information on OLEDs
- provide LED feedback
- support future firmware and hardware extension

---

## 3. Core Electrical Architecture

External power:
- 12V DC input

Generated rails:
- `+12V_SW` = switched 12V bus
- `+5V_LED` = generated from 12V
- `+3V3_LOGIC` = generated from 5V
- `+10V_MOTOR` = generated from 12V

Rail usage:
- `+10V_MOTOR` = TB6612 VM / fader motor rail
- `+5V_LED` = WS2812B power
- `+3V3_LOGIC` = Teensy + logic + OLED + TCA9548A + HC4067 + TB6612 logic VCC

---

## 4. Important Hardware Facts

### 4.1 Faders
Part:
- RSA0N11M9A0J

Known facts:
- 100 mm travel
- 10 kΩ potentiometer
- motor rated voltage = 10V DC
- motor max current = 800mA or less

Important conclusion:
- do not drive motor directly from 12V
- 5V is not preferred for normal motorized behavior
- use dedicated 10V rail

---

### 4.2 Motor drivers
Part:
- TB6612 × 3

Allocation:
- TB6612_1A → Fader1
- TB6612_1B → Fader2
- TB6612_2A → Fader3
- TB6612_2B → Fader4
- TB6612_3A → Fader5
- TB6612_3B → spare

Power:
- `VM → +10V_MOTOR`
- `VCC → +3V3_LOGIC`
- `STBY → +3V3_LOGIC`

---

### 4.3 OLED and I2C mux
Part:
- TCA9548A

Address:
- `0x70`

Address pin setting:
- A0 = GND
- A1 = GND
- A2 = GND

Reason:
- multiple OLEDs likely share the same I2C address
- TCA9548A isolates them by channel

Channel map:
- channel 0 → OLED1
- channel 1 → OLED2
- channel 2 → OLED3
- channel 3 → OLED4
- channel 4 → OLED5

---

### 4.4 LEDs
Part:
- WS2812B × 25

Power:
- `+5V_LED`

Data:
- one serial chain from Teensy Pin10 through a 330Ω resistor into LED1 DIN

---

### 4.5 Power converters
Buck converters:
- MP2315 #1 = 12V → 5V
- MP2315 #2 = 12V → 10V

LDO:
- AMS1117-3.3 = 5V → 3.3V

MP2315 symbol pin mapping used:
- Pin1 = AAM
- Pin2 = IN
- Pin3 = SW
- Pin4 = GND
- Pin5 = BST
- Pin6 = EN
- Pin7 = VCC
- Pin8 = FB

---

## 5. Important Pin Map

### 5.1 I2C
- Teensy Pin18 = SDA
- Teensy Pin19 = SCL

### 5.2 LED
- Teensy Pin10 = WS2812B data

### 5.3 Fader ADCs
- Pin14 = Fader1 ADC
- Pin15 = Fader2 ADC
- Pin16 = Fader3 ADC
- Pin17 = Fader4 ADC
- Pin20 = Fader5 ADC

### 5.4 TB6612 control pins
- Pin23 = DRV1_PWMA
- Pin41 = DRV1_AIN1
- Pin40 = DRV1_AIN2
- Pin22 = DRV1_PWMB
- Pin38 = DRV1_BIN1
- Pin39 = DRV1_BIN2

- Pin21 = DRV2_PWMA
- Pin37 = DRV2_AIN1
- Pin36 = DRV2_AIN2
- Pin13 = DRV2_PWMB
- Pin35 = DRV2_BIN1
- Pin34 = DRV2_BIN2

- Pin31 = DRV3_PWMA
- Pin32 = DRV3_AIN1
- Pin33 = DRV3_AIN2

---

## 6. Fader Electrical Model

Each fader has:
1. motor section
2. potentiometer section

Motor section:
- driven by TB6612 H-bridge

Potentiometer section:
- high end → 3.3V
- low end → GND
- wiper → Teensy ADC

Reason:
- ADC input range stays inside 0V to 3.3V

Optional analog filter:
- 100Ω series resistor
- 100nF to GND at ADC node

---

## 7. Design Constraints

1. 12V is only the upstream input rail.
2. 10V is dedicated to motor drive.
3. 3.3V is the logic rail.
4. 5V is the LED rail and LDO input.
5. MP2315 SW nodes are noisy and must be kept away from ADC and I2C traces.
6. TB6612 motor outputs are noisy and should not run near ADC traces.
7. OLED address conflict is solved through TCA9548A.
8. TB6612 STBY is assumed tied high to 3.3V.
9. Spare TB6612_3B channel is currently unused.

---

## 8. Firmware Assumptions

Firmware should assume:
- TCA9548A channel must be selected before OLED access
- WS2812B is a 25-LED serial chain
- each fader is closed-loop controlled using ADC + TB6612
- fader movement should use deadband and PWM limiting
- ADC values may require filtering

---

## 9. Important Documentation Files

Primary files:
- `docs/hardware-schematic-spec.md`
- `docs/pcb-layout-guide.md`
- `docs/pinout.md`
- `docs/fader-control.md`
- `docs/power-tree.md`
- `docs/bringup-checklist.md`
- `docs/net-naming-convention.md`
- `docs/connector-map.md`
- `docs/test-points.md`
- `docs/firmware-interface.md`
- `docs/mechanical-notes.md`

Use this file as the shortest high-value context pack for future AI sessions.

---

## 10. Best Prompting Tip for Future AI Use

If giving this project to another model, provide:
1. `docs/ai-context-pack.md`
2. `docs/hardware-schematic-spec.md`
3. `docs/pinout.md`
4. `docs/fader-control.md`

That set gives a strong baseline for:
- schematic reasoning
- firmware generation
- hardware review
- BOM extension
- PCB review