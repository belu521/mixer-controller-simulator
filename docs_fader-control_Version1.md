# Fader Control Architecture

## 1. Purpose

This document describes how the 5 motorized faders are electrically connected and how they are expected to be controlled in firmware.

---

## 2. Fader Hardware Model

Each fader has two separate functional sections:

### 2.1 Motor section
A DC motor moves the fader slider.

This is driven by:
- TB6612 H-bridge output

### 2.2 Position sensing section
A potentiometer reports the current slider position.

This is read by:
- Teensy ADC input

---

## 3. Fader Power Requirements

Fader model:
- RSA0N11M9A0J

Known key motor parameters:
- rated motor voltage: 10V DC
- max motor current: 800mA or less

Design rule:
- fader motor supply should be derived from `+10V_MOTOR`
- do not drive directly from 12V
- 5V motor drive is not recommended for normal operation

---

## 4. Driver Allocation

### TB6612_1
- channel A → Fader 1 motor
- channel B → Fader 2 motor

### TB6612_2
- channel A → Fader 3 motor
- channel B → Fader 4 motor

### TB6612_3
- channel A → Fader 5 motor
- channel B → spare

---

## 5. Electrical Mapping

## 5.1 Fader 1
### Motor
- `TB6612_1 AO1 → FADER1_MA`
- `TB6612_1 AO2 → FADER1_MB`

Control inputs:
- `PWMA ← Teensy Pin23`
- `AIN1 ← Teensy Pin41`
- `AIN2 ← Teensy Pin40`

### Position sensing
- pot high end → `+3V3_LOGIC`
- pot low end → `GND`
- pot wiper → `Teensy Pin14 (A0)`

---

## 5.2 Fader 2
### Motor
- `TB6612_1 BO1 → FADER2_MA`
- `TB6612_1 BO2 → FADER2_MB`

Control inputs:
- `PWMB ← Teensy Pin22`
- `BIN1 ← Teensy Pin38`
- `BIN2 ← Teensy Pin39`

### Position sensing
- pot high end → `+3V3_LOGIC`
- pot low end → `GND`
- pot wiper → `Teensy Pin15 (A1)`

---

## 5.3 Fader 3
### Motor
- `TB6612_2 AO1 → FADER3_MA`
- `TB6612_2 AO2 → FADER3_MB`

Control inputs:
- `PWMA ← Teensy Pin21`
- `AIN1 ← Teensy Pin37`
- `AIN2 ← Teensy Pin36`

### Position sensing
- pot high end → `+3V3_LOGIC`
- pot low end → `GND`
- pot wiper → `Teensy Pin16 (A2)`

---

## 5.4 Fader 4
### Motor
- `TB6612_2 BO1 → FADER4_MA`
- `TB6612_2 BO2 → FADER4_MB`

Control inputs:
- `PWMB ← Teensy Pin13`
- `BIN1 ← Teensy Pin35`
- `BIN2 ← Teensy Pin34`

### Position sensing
- pot high end → `+3V3_LOGIC`
- pot low end → `GND`
- pot wiper → `Teensy Pin17 (A3)`

---

## 5.5 Fader 5
### Motor
- `TB6612_3 AO1 → FADER5_MA`
- `TB6612_3 AO2 → FADER5_MB`

Control inputs:
- `PWMA ← Teensy Pin31`
- `AIN1 ← Teensy Pin32`
- `AIN2 ← Teensy Pin33`

### Position sensing
- pot high end → `+3V3_LOGIC`
- pot low end → `GND`
- pot wiper → `Teensy Pin20 (A6)`

---

## 6. TB6612 Power and Enable Rules

For every TB6612:
- `VM → +10V_MOTOR`
- `VCC → +3V3_LOGIC`
- `GND → GND`
- `STBY → +3V3_LOGIC`

Current design choice:
- STBY is tied high permanently
- drivers are always enabled when the board is powered

---

## 7. Motor Control Logic

Each TB6612 channel is controlled using:
- one PWM input
- two direction inputs

### 7.1 Forward
- `IN1 = 1`
- `IN2 = 0`
- `PWM = desired duty cycle`

### 7.2 Reverse
- `IN1 = 0`
- `IN2 = 1`
- `PWM = desired duty cycle`

### 7.3 Brake
- `IN1 = 1`
- `IN2 = 1`

### 7.4 Coast / stop
- `IN1 = 0`
- `IN2 = 0`
- `PWM = 0`

If the actual movement direction is opposite of expectation:
- swap motor wires
or
- invert control logic in firmware

---

## 8. Position Sensing Strategy

Each fader potentiometer is read as an analog voltage:
- low end = 0V
- high end = 3.3V
- wiper = variable voltage between 0 and 3.3V

This allows direct ADC reading on Teensy with no extra divider.

---

## 9. Optional ADC Filtering

Recommended optional filter per fader:
- 100Ω series resistor between wiper and ADC input
- 100nF from ADC input to GND

Purpose:
- reduce motor noise coupling
- smooth fast ADC jitter
- improve closed-loop stability

---

## 10. Firmware Control Concept

Typical per-fader control loop:

1. Read target position
2. Read actual ADC position
3. Compute error
4. If error is within deadband:
   - stop motor
5. If error is positive:
   - drive motor in one direction
6. If error is negative:
   - drive motor in the opposite direction
7. Use PWM magnitude based on error size

---

## 11. Recommended Closed-Loop Rules

### 11.1 Deadband
Use a small deadband to prevent hunting near target position.

### 11.2 Max PWM limit
Limit maximum PWM to avoid overly aggressive motion.

### 11.3 Soft approach
Reduce PWM when close to target to avoid overshoot.

### 11.4 Safety timeout
If a fader does not move as expected, stop the motor after a timeout.

---

## 12. Notes

1. The fader motor supply is a dedicated 10V rail.
2. The potentiometer sensing range is 0V to 3.3V.
3. ADC traces should be routed away from motor outputs and switching nodes.
4. One TB6612 channel remains unused for future expansion.