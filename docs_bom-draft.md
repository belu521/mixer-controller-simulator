# BOM Draft

## 1. Purpose

This document is a draft bill of materials for the motorized mixer controller board.

It is intended as:
- an engineering planning BOM
- a schematic capture reference
- a purchasing starting point
- an AI-readable hardware component summary

This is not yet a finalized manufacturing BOM.

---

## 2. Main Controller and Logic

| Ref Group | Part | Suggested Model | Package | Qty | Notes |
|---|---|---|---|---:|---|
| U_MCU | MCU module | Teensy 4.1 | module | 1 | main controller |
| U_I2C_MUX | I2C multiplexer | TCA9548APWR | TSSOP-24 | 1 | OLED bus mux |
| U_MUX1/U_MUX2 | analog mux | HC4067 | package depends on chosen source | 2 | expansion inputs |

---

## 3. Motor Driver Section

| Ref Group | Part | Suggested Model | Package | Qty | Notes |
|---|---|---|---|---:|---|
| U_DRV1..3 | motor driver | TB6612 | package depends on selected part | 3 | drives 5 faders total |
| FADER1..5 | motorized fader | RSA0N11M9A0J | mechanical assembly | 5 | 10V motorized fader |

---

## 4. Power Input Section

| Ref Group | Part | Suggested Model | Package | Qty | Notes |
|---|---|---|---|---:|---|
| J_PWR | DC power jack | DC-005-5A-2.5 or equivalent | THT / panel PCB | 1 | 12V input |
| SW_PWR | rocker switch | SS01-BBIWL-RP20-R | THT / panel PCB | 1 | main power switch |

---

## 5. Buck Converter Section

| Ref Group | Part | Suggested Model | Package | Qty | Notes |
|---|---|---|---|---:|---|
| U_BUCK_5V | buck converter IC | MP2315SGJ-Z | SOP-8 | 1 | 12V → 5V |
| U_BUCK_10V | buck converter IC | MP2315SGJ-Z | SOP-8 | 1 | 12V → 10V |
| U_LDO_3V3 | LDO regulator | AMS1117-3.3 | SOT-223 or equivalent | 1 | 5V → 3.3V |

---

## 6. Inductors

| Ref Group | Part | Value | Rating | Qty | Notes |
|---|---|---|---|---:|---|
| L_5V | power inductor | 10uH | ≥3A | 1 | 5V buck |
| L_10V | power inductor | 10uH | ≥5A | 1 | 10V motor buck |

---

## 7. Diodes

| Ref Group | Part | Suggested Model | Package | Qty | Notes |
|---|---|---|---|---:|---|
| D_BUCK_5V | Schottky diode | SS34 | SOD-123 / SMB depending on choice | 1 | 5V buck freewheel |
| D_BUCK_10V | Schottky diode | SS34 | SOD-123 / SMB depending on choice | 1 | 10V buck freewheel |

---

## 8. Displays and LEDs

| Ref Group | Part | Suggested Model | Package | Qty | Notes |
|---|---|---|---|---:|---|
| OLED1..5 | OLED module | 0.96 inch I2C OLED | module | 5 | likely SSD1306 type |
| LED1..25 | RGB LED | WS2812B | 5050 or chosen variant | 25 | indicator LEDs |

---

## 9. Feedback and Pull-Up Resistors

## 9.1 Buck feedback resistors
| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| R_FB_5V_TOP | 100kΩ | 0402 / 0603 | 1 | MP2315 5V top divider |
| R_FB_5V_BOT | 20kΩ | 0402 / 0603 | 1 | MP2315 5V bottom divider |
| R_FB_10V_TOP | 100kΩ | 0402 / 0603 | 1 | MP2315 10V top divider |
| R_FB_10V_BOT | 8.2kΩ | 0402 / 0603 | 1 | MP2315 10V bottom divider |

## 9.2 I2C pull-up resistors
| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| R_I2C_SDA | 4.7kΩ | 0402 / 0603 | 1 | main I2C pull-up |
| R_I2C_SCL | 4.7kΩ | 0402 / 0603 | 1 | main I2C pull-up |

## 9.3 LED data resistor
| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| R_LED_IN | 330Ω | 0402 / 0603 | 1 | between Teensy and LED1 DIN |

## 9.4 Optional ADC filter resistors
| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| R_FADER_ADC1..5 | 100Ω | 0402 / 0603 | 5 | optional ADC series filter |

---

## 10. Capacitors

## 10.1 Known usable capacitor examples
| Part | Description | Notes |
|---|---|---|
| HGC1206R5107M100NSPJ | 100uF / 10V / 1206 | usable as bulk capacitor in suitable locations |
| CGA0603X7R104K500JT | 100nF / 50V / X7R / 0603 | general decoupling and HF filtering |

---

## 10.2 Buck converter capacitors
| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| C_BUCK_5V_IN | 10uF | 0805 / suitable | 1 | input capacitor |
| C_BUCK_5V_BOOT | 100nF | 0402 / 0603 | 1 | BST capacitor |
| C_BUCK_5V_OUT_BULK | 100uF | suitable | 1 | output bulk |
| C_BUCK_5V_OUT_HF | 100nF | 0402 / 0603 | 1 | output HF |

| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| C_BUCK_10V_IN | 10uF | 0805 / suitable | 1 | input capacitor |
| C_BUCK_10V_BOOT | 100nF | 0402 / 0603 | 1 | BST capacitor |
| C_BUCK_10V_OUT_BULK | 100uF | suitable | 1 | output bulk |
| C_BUCK_10V_OUT_HF | 100nF | 0402 / 0603 | 1 | output HF |

---

## 10.3 LDO capacitors
| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| C_3V3_IN | 10uF | suitable | 1 | AMS1117 input |
| C_3V3_OUT1 | 10uF | suitable | 1 | AMS1117 output |
| C_3V3_OUT2 | 100nF | 0402 / 0603 | 1 | AMS1117 output HF |

---

## 10.4 TB6612 local decoupling
Per TB6612:
- 100uF bulk × 1
- 100nF VM × 1
- 100nF VCC × 1

Total for 3 drivers:
| Ref Group | Value | Qty | Notes |
|---|---|---:|---|
| C_DRV_VM_BULK | 100uF | 3 | one per TB6612 |
| C_DRV_VM_HF | 100nF | 3 | one per TB6612 VM |
| C_DRV_VCC_HF | 100nF | 3 | one per TB6612 VCC |

---

## 10.5 OLED decoupling
| Ref Group | Value | Qty | Notes |
|---|---|---:|---|
| C_OLED1..5 | 100nF | 5 | one per OLED |

---

## 10.6 WS2812B rail decoupling
Recommended per 5 LEDs:
- 100uF × 1
- 100nF × 1

For 25 LEDs total:
| Ref Group | Value | Qty | Notes |
|---|---|---:|---|
| C_LED_BULK_GROUP | 100uF | 5 | one per LED group |
| C_LED_HF_GROUP | 100nF | 5 | one per LED group |

---

## 10.7 Optional ADC filter capacitors
| Ref Group | Value | Package | Qty | Notes |
|---|---|---|---:|---|
| C_FADER_ADC1..5 | 100nF | 0402 / 0603 | 5 | optional ADC RC filter |

---

## 11. Connectors / Headers / Interfaces

| Ref Group | Part | Qty | Notes |
|---|---|---:|---|
| J_FADER1..5 | fader connectors or direct footprint | 5 | depends on mechanical design |
| J_OLED1..5 | OLED connectors or direct module headers | 5 | depends on module type |
| J_DEBUG | debug/program header if needed | 1 | optional |
| TP_* | test points | as needed | recommended for 12V/10V/5V/3.3V/GND/I2C |

---

## 12. Estimated Design Blocks Summary

| Block | Qty |
|---|---:|
| Teensy 4.1 | 1 |
| TCA9548A | 1 |
| HC4067 | 2 |
| TB6612 | 3 |
| MP2315 | 2 |
| AMS1117-3.3 | 1 |
| Motorized fader | 5 |
| OLED | 5 |
| WS2812B | 25 |
| Main power switch | 1 |
| DC jack | 1 |

---

## 13. Notes

1. Final package selection should match PCB assembly preference.
2. TB6612 exact package variant should be fixed before PCB footprint creation.
3. Capacitor voltage ratings must be checked against actual rail voltage.
4. Motor rail components must be chosen for current margin, not just nominal values.
5. This file is a draft and should later be split into:
   - engineering BOM
   - purchasing BOM
   - assembly BOM