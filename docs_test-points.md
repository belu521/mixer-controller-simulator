# Test Points

## 1. Purpose

This document defines recommended PCB test points for debugging, validation, bring-up, and future maintenance.

Test points should be added for:
- major power rails
- common ground
- key communications buses
- critical control signals if practical

---

## 2. General Rules

1. Every major rail should have at least one test point.
2. Ground should have multiple accessible test points.
3. Test points should be easy to reach with a multimeter probe.
4. Prefer placing them near the related subsystem.
5. If space allows, label them on silkscreen.

---

## 3. Required Power Test Points

## 3.1 Input rail
Suggested name:
- `TP_12V_IN`

Signal:
- `+12V_IN`

Purpose:
- verify incoming supply at DC jack

---

## 3.2 Switched 12V
Suggested name:
- `TP_12V_SW`

Signal:
- `+12V_SW`

Purpose:
- verify switch output
- confirm main board power distribution

---

## 3.3 5V rail
Suggested name:
- `TP_5V`

Signal:
- `+5V_LED`

Purpose:
- validate MP2315 5V converter output
- validate LED supply rail

---

## 3.4 3.3V rail
Suggested name:
- `TP_3V3`

Signal:
- `+3V3_LOGIC`

Purpose:
- validate AMS1117 output
- logic rail measurement

---

## 3.5 10V motor rail
Suggested name:
- `TP_10V`

Signal:
- `+10V_MOTOR`

Purpose:
- validate motor supply converter output
- measure under motor load

---

## 3.6 Ground
Suggested names:
- `TP_GND_1`
- `TP_GND_2`
- `TP_GND_3`

Signal:
- `GND`

Purpose:
- probing reference
- convenient measurements across board

Recommended:
- one near power input
- one near logic section
- one near motor driver section

---

## 4. I2C Test Points

Suggested names:
- `TP_SDA`
- `TP_SCL`

Signals:
- `I2C_SDA`
- `I2C_SCL`

Purpose:
- scope/debug I2C bus
- verify pull-up behavior
- diagnose OLED/TCA issues

Optional:
- add near Teensy/TCA9548A area

---

## 5. LED Data Test Point

Suggested name:
- `TP_LED_DATA`

Signal:
- `LED_DATA`

Purpose:
- verify WS2812B drive waveform
- debug first LED input problems

Place:
- near Teensy output / series resistor / first LED input

---

## 6. ADC / Fader Test Points

Recommended optional test points:
- `TP_FADER1_ADC`
- `TP_FADER2_ADC`
- `TP_FADER3_ADC`
- `TP_FADER4_ADC`
- `TP_FADER5_ADC`

Purpose:
- measure raw analog voltage
- debug noisy or incorrect position sensing
- compare mechanical position vs ADC voltage

If board space is limited:
- at least add one or two representative ADC test points

---

## 7. TB6612 Related Optional Test Points

Optional signals:
- `TP_DRV1_PWMA`
- `TP_DRV1_AIN1`
- `TP_DRV1_AIN2`
- `TP_DRV2_PWMA`
- `TP_DRV3_PWMA`

Purpose:
- firmware debugging
- confirm PWM and direction behavior

These are optional because large quantities of logic test points can consume space.

---

## 8. Recommended Minimum Test Point Set

At minimum, add:
- `TP_12V_IN`
- `TP_12V_SW`
- `TP_5V`
- `TP_3V3`
- `TP_10V`
- `TP_GND_1`
- `TP_SDA`
- `TP_SCL`
- `TP_LED_DATA`

This minimum set gives strong board-level debug coverage.

---

## 9. Recommended Placement Strategy

### Near power section
- `TP_12V_IN`
- `TP_12V_SW`
- `TP_5V`
- `TP_10V`
- one GND

### Near logic section
- `TP_3V3`
- `TP_SDA`
- `TP_SCL`
- another GND

### Near LED chain
- `TP_LED_DATA`

### Near fader area
- selected `TP_FADERx_ADC`
- optional motor-driver-related test points

---

## 10. Labeling Recommendation

Use silkscreen labels exactly matching documentation, e.g.:
- `12VIN`
- `12VSW`
- `5V`
- `3V3`
- `10V`
- `GND`
- `SDA`
- `SCL`
- `LED`
- `F1`
- `F2`

Short labels may be used on PCB while full names remain in docs.

---

## 11. Final Notes

1. Power rail test points are mandatory.
2. At least one reliable ground test point is mandatory.
3. I2C test points are strongly recommended.
4. ADC test points are very useful during fader tuning.
5. Keep test points physically accessible even after assembly if possible.