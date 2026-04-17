# Connector Map

## 1. Purpose

This document defines the external connectors, module interfaces, and recommended pin groupings for the motorized mixer controller board.

It is intended for:
- schematic capture
- PCB connector placement
- wiring harness design
- assembly planning
- firmware / hardware integration reference

---

## 2. Connector Strategy

The board contains several connection types:

1. Power input connector
2. Fader motor + potentiometer connections
3. OLED connections
4. Optional debug / programming headers
5. Optional test interfaces

Connector selection depends on:
- board form factor
- whether modules are PCB-mounted directly or via cables
- final mechanical enclosure

---

## 3. Power Input Connector

## 3.1 DC Jack
Recommended:
- board-mounted DC jack
- example: DC-005-5A-2.5 or equivalent

### Pin mapping
- `Pin1 = +12V_IN`
- `Pin2 = GND`
- `Pin3 = NC`

### Notes
- place near board edge
- keep path short to power switch
- reinforce surrounding copper for mechanical strength

---

## 4. Power Switch Interface

## 4.1 Main power switch
Recommended:
- SPST rocker or toggle type

### Connections
- `COM ← +12V_IN`
- `NO → +12V_SW`

### Notes
- can be PCB-mounted or panel-wired
- if panel-wired, consider locking connector or labeled wire pads

---

## 5. Fader Connectors

Each motorized fader requires:
- 2 motor terminals
- 3 potentiometer terminals

Total:
- 5 signals per fader

Recommended logical grouping per fader:
1. Motor A
2. Motor B
3. Pot high
4. Pot wiper
5. Pot low

---

## 5.1 Fader 1 connector
Suggested name:
- `J_FADER1`

### Pin mapping
1. `FADER1_MA`
2. `FADER1_MB`
3. `+3V3_LOGIC`
4. `FADER1_ADC`
5. `GND`

---

## 5.2 Fader 2 connector
Suggested name:
- `J_FADER2`

### Pin mapping
1. `FADER2_MA`
2. `FADER2_MB`
3. `+3V3_LOGIC`
4. `FADER2_ADC`
5. `GND`

---

## 5.3 Fader 3 connector
Suggested name:
- `J_FADER3`

### Pin mapping
1. `FADER3_MA`
2. `FADER3_MB`
3. `+3V3_LOGIC`
4. `FADER3_ADC`
5. `GND`

---

## 5.4 Fader 4 connector
Suggested name:
- `J_FADER4`

### Pin mapping
1. `FADER4_MA`
2. `FADER4_MB`
3. `+3V3_LOGIC`
4. `FADER4_ADC`
5. `GND`

---

## 5.5 Fader 5 connector
Suggested name:
- `J_FADER5`

### Pin mapping
1. `FADER5_MA`
2. `FADER5_MB`
3. `+3V3_LOGIC`
4. `FADER5_ADC`
5. `GND`

---

## 5.6 Fader connector notes

### Electrical notes
- motor pins carry switching current
- ADC pin is sensitive and should be routed away from motor outputs
- 3.3V and GND should be stable and low-noise

### Mechanical notes
- if faders are mounted directly on PCB, the “connector” may just be the footprint pin assignment
- if wired off-board, use keyed connectors to avoid reversal

---

## 6. OLED Connectors

Each OLED module typically uses 4 pins:
1. GND
2. VCC
3. SCL
4. SDA

Recommended logical connector per display:
- `J_OLED1` through `J_OLED5`

---

## 6.1 OLED1 connector
Suggested name:
- `J_OLED1`

### Pin mapping
1. `GND`
2. `+3V3_LOGIC`
3. `OLED1_SCL`
4. `OLED1_SDA`

---

## 6.2 OLED2 connector
Suggested name:
- `J_OLED2`

### Pin mapping
1. `GND`
2. `+3V3_LOGIC`
3. `OLED2_SCL`
4. `OLED2_SDA`

---

## 6.3 OLED3 connector
Suggested name:
- `J_OLED3`

### Pin mapping
1. `GND`
2. `+3V3_LOGIC`
3. `OLED3_SCL`
4. `OLED3_SDA`

---

## 6.4 OLED4 connector
Suggested name:
- `J_OLED4`

### Pin mapping
1. `GND`
2. `+3V3_LOGIC`
3. `OLED4_SCL`
4. `OLED4_SDA`

---

## 6.5 OLED5 connector
Suggested name:
- `J_OLED5`

### Pin mapping
1. `GND`
2. `+3V3_LOGIC`
3. `OLED5_SCL`
4. `OLED5_SDA`

---

## 6.6 OLED connector notes
- each OLED is isolated at the bus level by TCA9548A
- each module should have local 100nF decoupling
- keep SCL/SDA grouped as a pair where possible

---

## 7. Teensy Interface Considerations

If Teensy 4.1 is:
- socketed: provide headers or board socket
- directly soldered: document orientation clearly

Recommended to expose or clearly label:
- GND
- 3.3V
- program/reset access if needed
- USB access if relevant mechanically

---

## 8. Optional Debug / Programming Header

Suggested name:
- `J_DEBUG`

Suggested signals:
1. `GND`
2. `+3V3_LOGIC`
3. `I2C_SDA`
4. `I2C_SCL`
5. `UART_TX` if used
6. `UART_RX` if used
7. `RESET` if accessible

This is optional and depends on firmware workflow.

---

## 9. Optional Test/Service Header

Suggested name:
- `J_SERVICE`

Possible signals:
1. `GND`
2. `+12V_SW`
3. `+10V_MOTOR`
4. `+5V_LED`
5. `+3V3_LOGIC`

This can be replaced with individual test points.

---

## 10. Recommended Connector Labeling Rules

1. Use stable block names:
   - `J_FADER1`
   - `J_OLED3`
   - `J_DEBUG`
2. Put pin 1 markers clearly on PCB silkscreen.
3. Use consistent left-to-right or top-to-bottom pin ordering.
4. Keep power pins grouped logically.
5. Avoid mixing motor pins between neighboring faders.

---

## 11. Summary Table

| Connector | Purpose | Main signals |
|---|---|---|
| J_PWR | 12V input | +12V_IN, GND |
| SW_PWR | power control | +12V_IN, +12V_SW |
| J_FADER1..5 | fader connections | motor pair, 3.3V, ADC, GND |
| J_OLED1..5 | OLED modules | GND, 3.3V, SCL, SDA |
| J_DEBUG | optional debug | GND, 3.3V, I2C, UART, reset |
| J_SERVICE | optional service header | rail monitoring signals |