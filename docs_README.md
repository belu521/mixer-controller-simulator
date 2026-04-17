# Hardware Documentation Index

## 1. Purpose

This directory contains the hardware design documentation for the motorized mixer controller board.

The documents here are intended for:
- hardware design
- schematic capture
- PCB layout
- firmware integration
- bring-up and debugging
- future maintainers
- AI model parsing and reasoning

---

## 2. Document List

### `hardware-schematic-spec.md`
Main schematic-level hardware specification.

Contains:
- system overview
- power rail architecture
- major component roles
- fader wiring
- TB6612 wiring
- TCA9548A and OLED architecture
- WS2812B architecture
- key design constraints

Use this as the primary hardware reference.

---

### `pcb-layout-guide.md`
PCB placement and routing guidance.

Contains:
- PCB zoning
- high-current routing rules
- noisy vs sensitive area separation
- grounding strategy
- trace width guidance
- buck converter layout rules
- ADC / I2C routing guidance

Use this during PCB layout.

---

### `pinout.md`
Current pin assignment reference.

Contains:
- confirmed Teensy pin mapping
- TB6612 control pin allocation
- fader ADC pin mapping
- I2C pin mapping
- high-level rail naming summary

Use this when connecting schematic symbols and firmware definitions.

---

### `fader-control.md`
Motorized fader hardware and firmware interaction guide.

Contains:
- per-fader motor wiring
- per-fader ADC wiring
- TB6612 channel allocation
- motor direction logic
- position sensing rules
- optional ADC filtering
- closed-loop control concept

Use this for both hardware and firmware work related to fader motion.

---

### `power-tree.md`
Board power distribution overview.

Contains:
- full rail generation hierarchy
- source-to-consumer mapping
- current/load considerations
- rail constraints
- validation sequence for power rails

Use this when validating power architecture and board bring-up.

---

### `bringup-checklist.md`
Hardware bring-up procedure.

Contains:
- inspection checklist
- staged power-up sequence
- buck regulator validation
- logic rail validation
- I2C/OLED validation
- WS2812B validation
- ADC validation
- motor driver test sequence
- closed-loop fader test guidance

Use this when powering the board for the first time.

---

### `net-naming-convention.md`
Net naming rules for schematic and PCB.

Contains:
- power net naming
- OLED/I2C net naming
- LED chain naming
- fader motor and ADC net naming
- TB6612 control net naming
- naming style rules

Use this to keep the schematic and PCB naming consistent.

---

## 3. Recommended Reading Order

For a new contributor, recommended reading order is:

1. `hardware-schematic-spec.md`
2. `pinout.md`
3. `power-tree.md`
4. `fader-control.md`
5. `pcb-layout-guide.md`
6. `bringup-checklist.md`
7. `net-naming-convention.md`

---

## 4. Suggested Usage by Role

### Hardware schematic designer
Read:
- `hardware-schematic-spec.md`
- `pinout.md`
- `net-naming-convention.md`

### PCB designer
Read:
- `pcb-layout-guide.md`
- `power-tree.md`
- `net-naming-convention.md`

### Firmware developer
Read:
- `pinout.md`
- `fader-control.md`
- `hardware-schematic-spec.md`

### Bring-up / debug engineer
Read:
- `bringup-checklist.md`
- `power-tree.md`
- `hardware-schematic-spec.md`

### AI model / automation workflow
Best starting points:
- `hardware-schematic-spec.md`
- `pinout.md`
- `fader-control.md`
- `net-naming-convention.md`

---

## 5. Current Hardware Summary

Main controller:
- Teensy 4.1

Main peripherals:
- 5 motorized faders
- 3 TB6612 motor drivers
- 5 OLED displays
- 1 TCA9548A
- 25 WS2812B LEDs
- 2 HC4067 expansion devices

Power architecture:
- 12V DC input
- 12V → 5V
- 12V → 10V
- 5V → 3.3V

Design principles:
- 10V rail for fader motors
- 3.3V rail for logic
- 5V rail for WS2812B
- TCA9548A used to avoid OLED address conflict

---

## 6. Suggested Next Documentation

Future documents that may be useful:

- `bom-draft.md`
- `connector-map.md`
- `mechanical-notes.md`
- `test-points.md`
- `firmware-interface.md`

---

## 7. Maintenance Notes

When updating hardware:
1. update `pinout.md` if pins change
2. update `power-tree.md` if rails or loads change
3. update `hardware-schematic-spec.md` for architecture changes
4. update `bringup-checklist.md` if validation flow changes
5. keep net names aligned with `net-naming-convention.md`

This helps keep schematic, PCB, firmware, and documentation synchronized.