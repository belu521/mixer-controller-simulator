# PCB Layout Guide

## 1. Purpose

This document describes practical PCB placement and routing rules for the motorized mixer controller board.

It focuses on:
- module placement
- power routing
- noisy vs sensitive areas
- trace width
- filtering placement
- grounding strategy

---

## 2. Recommended PCB Functional Zones

The PCB should be divided into these zones:

### 2.1 Power input zone
Contains:
- DC jack
- power switch
- 12V input routing
- input bulk filtering

Place this at the PCB edge.

### 2.2 Buck converter zone
Contains:
- MP2315 12V→5V
- MP2315 12V→10V
- inductors
- Schottky diodes
- feedback resistors
- input/output capacitors

This zone should stay close to the power input zone.

### 2.3 Logic and controller zone
Contains:
- Teensy 4.1
- TCA9548A
- HC4067
- low-noise logic signals
- ADC filters

Keep this zone electrically quiet.

### 2.4 Motor driver zone
Contains:
- TB6612 × 3
- VM decoupling capacitors
- motor routing to faders

Place this near the fader connections.

### 2.5 Display and LED zone
Contains:
- OLED interfaces
- WS2812B LED chain
- LED decoupling capacitors

Arrange based on front panel layout.

---

## 3. Global Layout Principles

1. Keep high-current loops short.
2. Keep switching nodes compact.
3. Separate noisy power circuitry from ADC and I2C.
4. Use a solid ground plane.
5. Route sensitive analog traces away from motors and buck converters.
6. Place decoupling capacitors close to the load pins.

---

## 4. Power Input Routing

### 4.1 DC jack
- Place at board edge.
- Route `+12V_IN` directly to power switch.
- Route `GND` directly into main ground copper.

### 4.2 Power switch
- Place close to DC jack.
- Route:
  - `+12V_IN → switch COM`
  - `switch NO → +12V_SW`

### 4.3 Trace width
Use at least:
- `+12V_IN`: 2.0 mm
- `+12V_SW`: 2.0 mm

---

## 5. MP2315 Layout Rules

## 5.1 Critical rule
The most important node is `SW`.

Keep:
- SW copper area small
- SW to inductor short
- BST capacitor close to BST and SW
- input capacitor close to IN/VCC
- output capacitor close to inductor output

Do not route:
- ADC traces
- I2C traces
- OLED lines
under or near the SW region

---

## 5.2 12V→5V converter placement
Recommended order:

`12V input capacitor → MP2315 → inductor → output capacitor → 5V rail`

Keep the diode tight to:
- SW
- GND

Feedback resistors:
- place close to FB pin
- keep FB trace away from SW

---

## 5.3 12V→10V converter placement
Same rules as 5V converter, but pay extra attention to current handling.

Recommended:
- wider output copper
- strong output decoupling
- short path to TB6612 VM distribution

Use at least:
- `+10V_MOTOR`: 2.0 mm or wider

---

## 6. AMS1117 Layout Rules

- Place near logic power distribution area.
- Place output capacitor close to regulator.
- Feed 3.3V rail outward from regulator output.
- Avoid routing motor return current through the logic regulator area.

---

## 7. Teensy and Logic Area Rules

### 7.1 Teensy placement
- Place in a low-noise zone.
- Keep away from:
  - MP2315 SW nodes
  - TB6612 motor outputs
  - LED power surge distribution

### 7.2 TCA9548A placement
- Place near Teensy.
- Keep I2C host traces short.
- Fan out OLED channel lines toward display connectors.

### 7.3 HC4067 placement
- Place near other logic/ADC-related areas, not near motor output lines.

---

## 8. TB6612 Layout Rules

### 8.1 Placement
- Place all TB6612 chips near the fader motor connection area.
- Keep motor output traces short.

### 8.2 VM decoupling
Per TB6612:
- place 100nF very close to VM pin
- place 100uF nearby as bulk capacitor
- place 100nF close to VCC pin

### 8.3 Routing
- motor output traces should be short and moderately wide
- avoid running motor traces parallel to ADC traces

Recommended widths:
- motor outputs: 1.0 mm to 1.5 mm
- VM rail feeding drivers: 2.0 mm or wider

---

## 9. Fader Potentiometer ADC Routing

The fader wiper traces are analog signals and should be treated as sensitive.

### Rules
- keep them short
- avoid running beside motor lines
- avoid running near SW nodes
- keep a continuous ground reference below
- if possible, add simple RC filtering near ADC input

Recommended optional filter:
- 100Ω series resistor
- 100nF to ground at ADC side

---

## 10. OLED Routing Rules

- Route each OLED through its dedicated TCA9548A channel.
- Keep I2C traces short if possible.
- If OLEDs are distributed across the board, keep SDA/SCL pair together.
- Each OLED should have local 100nF decoupling.

---

## 11. WS2812B Routing Rules

### 11.1 Data line
- `Teensy Pin10 → 330Ω → LED1 DIN`
- Keep first data trace short.
- Avoid running LED data parallel to noisy motor lines.

### 11.2 Power
- Do not use a thin daisy-chained power trace for all LEDs.
- Use a proper 5V/GND distribution rail.
- Inject power at multiple locations if LEDs are spread out.

### 11.3 Decoupling
For every 5 LEDs:
- 100uF bulk capacitor
- 100nF high-frequency capacitor

---

## 12. Grounding Strategy

### 12.1 Use a solid ground plane
At least one layer should provide an uninterrupted ground reference where possible.

### 12.2 High-current return management
Motor and buck converter return currents should return locally and not cross the analog sensing area.

### 12.3 Sensitive areas
ADC, FB divider, and I2C should have a quiet ground reference.

---

## 13. Trace Width Recommendations

### High current
- `+12V_IN`: ≥ 2.0 mm
- `+12V_SW`: ≥ 2.0 mm
- `+10V_MOTOR`: ≥ 2.0 mm
- `+5V_LED` main trunk: 1.5 mm to 2.0 mm
- TB6612 motor outputs: 1.0 mm to 1.5 mm

### Logic and signal
- GPIO: 0.2 mm to 0.25 mm
- I2C: 0.2 mm to 0.25 mm
- ADC traces: 0.2 mm to 0.25 mm

---

## 14. High-Risk Noise Nodes

### 14.1 MP2315 SW
Highest noise area on the board.

### 14.2 TB6612 outputs
PWM motor drive outputs create switching noise.

### 14.3 LED power rail
Can generate high transient current when many LEDs switch state.

Avoid routing sensitive signals near these regions.

---

## 15. Recommended Placement Order Example

For a long mixer-style board:

1. DC jack
2. power switch
3. 12V power conditioning
4. MP2315 power area
5. AMS1117
6. Teensy
7. TCA9548A / HC4067
8. TB6612 drivers
9. fader connections
10. OLEDs / LEDs according to front panel layout

---

## 16. Final PCB Checklist

- [ ] DC jack and switch placed at board edge
- [ ] 12V traces wide enough
- [ ] MP2315 SW loops compact
- [ ] TB6612 VM caps close to VM pins
- [ ] ADC traces away from motor outputs
- [ ] I2C traces away from buck switch nodes
- [ ] LED power distribution reinforced
- [ ] solid ground plane used
- [ ] 10V rail routed cleanly to motor drivers
- [ ] feedback divider traces kept quiet