# Net Naming Convention

## 1. Purpose

This document defines a consistent net naming scheme for the schematic and PCB.

Consistent names improve:
- schematic readability
- PCB review
- firmware understanding
- AI model parsing
- future maintenance

---

## 2. Power Nets

- `+12V_IN` = raw DC jack positive input
- `+12V_SW` = switched 12V rail
- `+5V_LED` = 5V rail from MP2315
- `+3V3_LOGIC` = 3.3V logic rail
- `+10V_MOTOR` = 10V motor rail
- `GND` = common ground

---

## 3. Main I2C Nets

- `I2C_SDA`
- `I2C_SCL`

Used between:
- Teensy
- TCA9548A

---

## 4. OLED Channel Nets

- `OLED1_SDA`
- `OLED1_SCL`
- `OLED2_SDA`
- `OLED2_SCL`
- `OLED3_SDA`
- `OLED3_SCL`
- `OLED4_SDA`
- `OLED4_SCL`
- `OLED5_SDA`
- `OLED5_SCL`

---

## 5. LED Nets

- `LED_DATA`
- `LED1_DOUT`
- `LED2_DOUT`
- `LED3_DOUT`
- ...
- `LED24_DOUT`

---

## 6. Fader Motor Nets

- `FADER1_MA`
- `FADER1_MB`
- `FADER2_MA`
- `FADER2_MB`
- `FADER3_MA`
- `FADER3_MB`
- `FADER4_MA`
- `FADER4_MB`
- `FADER5_MA`
- `FADER5_MB`

---

## 7. Fader ADC Nets

- `FADER1_ADC`
- `FADER2_ADC`
- `FADER3_ADC`
- `FADER4_ADC`
- `FADER5_ADC`

---

## 8. TB6612 Control Nets

### Driver 1
- `DRV1_PWMA`
- `DRV1_AIN1`
- `DRV1_AIN2`
- `DRV1_PWMB`
- `DRV1_BIN1`
- `DRV1_BIN2`

### Driver 2
- `DRV2_PWMA`
- `DRV2_AIN1`
- `DRV2_AIN2`
- `DRV2_PWMB`
- `DRV2_BIN1`
- `DRV2_BIN2`

### Driver 3
- `DRV3_PWMA`
- `DRV3_AIN1`
- `DRV3_AIN2`
- `DRV3_PWMB`
- `DRV3_BIN1`
- `DRV3_BIN2`

---

## 9. Feedback and Power Support Nets

Recommended names:
- `FB_5V_NODE`
- `FB_10V_NODE`
- `LED_5V_INJECT_1`
- `LED_5V_INJECT_2`
- `LED_5V_INJECT_3`
- `LED_5V_INJECT_4`
- `LED_5V_INJECT_5`

---

## 10. Naming Rules

1. Use uppercase letters.
2. Use underscores between words.
3. Use consistent numbering for repeated blocks.
4. Use explicit function-based names.
5. Avoid vague names like `NET1`, `SIG_A`, `TEST2`.

Good examples:
- `FADER3_ADC`
- `DRV2_AIN1`
- `OLED4_SCL`

Bad examples:
- `IO17`
- `LINE2`
- `CTRL_A`

---

## 11. Benefits

Using this naming scheme helps:
- firmware pin map generation
- easier schematic review
- more readable PCB annotations
- easier AI-assisted hardware reasoning