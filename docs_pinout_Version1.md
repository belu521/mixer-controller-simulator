# Pinout Reference

## 1. Purpose

This document defines the current confirmed pin assignments for the Teensy 4.1 and related external hardware connections.

---

## 2. Teensy 4.1 Confirmed Pin Usage

## 2.1 I2C
- `Pin18` = `I2C_SDA`
- `Pin19` = `I2C_SCL`

Used for:
- TCA9548A main I2C bus

---

## 2.2 WS2812B
- `Pin10` = `LED_DATA`

Used for:
- WS2812B LED chain input

Connection:
- `Pin10 → 330Ω → LED1 DIN`

---

## 2.3 Fader ADC Inputs
- `Pin14 (A0)` = `FADER1_ADC`
- `Pin15 (A1)` = `FADER2_ADC`
- `Pin16 (A2)` = `FADER3_ADC`
- `Pin17 (A3)` = `FADER4_ADC`
- `Pin20 (A6)` = `FADER5_ADC`

Used for:
- motorized fader position sensing

---

## 2.4 TB6612 Driver Control Pins

### TB6612_1
#### A channel
- `Pin23` = `DRV1_PWMA`
- `Pin41` = `DRV1_AIN1`
- `Pin40` = `DRV1_AIN2`

#### B channel
- `Pin22` = `DRV1_PWMB`
- `Pin38` = `DRV1_BIN1`
- `Pin39` = `DRV1_BIN2`

### TB6612_2
#### A channel
- `Pin21` = `DRV2_PWMA`
- `Pin37` = `DRV2_AIN1`
- `Pin36` = `DRV2_AIN2`

#### B channel
- `Pin13` = `DRV2_PWMB`
- `Pin35` = `DRV2_BIN1`
- `Pin34` = `DRV2_BIN2`

### TB6612_3
#### A channel
- `Pin31` = `DRV3_PWMA`
- `Pin32` = `DRV3_AIN1`
- `Pin33` = `DRV3_AIN2`

#### B channel
- currently unused / spare

---

## 3. Fader Mapping

### Fader 1
Motor driver:
- TB6612_1 A channel

ADC:
- `Pin14 (A0)`

### Fader 2
Motor driver:
- TB6612_1 B channel

ADC:
- `Pin15 (A1)`

### Fader 3
Motor driver:
- TB6612_2 A channel

ADC:
- `Pin16 (A2)`

### Fader 4
Motor driver:
- TB6612_2 B channel

ADC:
- `Pin17 (A3)`

### Fader 5
Motor driver:
- TB6612_3 A channel

ADC:
- `Pin20 (A6)`

---

## 4. TCA9548A Pin Context

### Main I2C
- `SDA ← Teensy Pin18`
- `SCL ← Teensy Pin19`

### Address configuration
- `A0 = GND`
- `A1 = GND`
- `A2 = GND`

Address:
- `0x70`

### OLED channels
- Channel 0 → OLED1
- Channel 1 → OLED2
- Channel 2 → OLED3
- Channel 3 → OLED4
- Channel 4 → OLED5

---

## 5. Power Rail Summary

- `+12V_IN` = DC jack raw input
- `+12V_SW` = switched 12V rail
- `+5V_LED` = 5V generated rail
- `+3V3_LOGIC` = 3.3V logic rail
- `+10V_MOTOR` = 10V motor rail
- `GND` = common ground

---

## 6. TB6612 to Fader Mapping Table

| Fader | Driver | Channel | PWM Pin | IN1 Pin | IN2 Pin | ADC Pin |
|------|--------|---------|---------|---------|---------|--------|
| 1 | TB6612_1 | A | Pin23 | Pin41 | Pin40 | Pin14 |
| 2 | TB6612_1 | B | Pin22 | Pin38 | Pin39 | Pin15 |
| 3 | TB6612_2 | A | Pin21 | Pin37 | Pin36 | Pin16 |
| 4 | TB6612_2 | B | Pin13 | Pin35 | Pin34 | Pin17 |
| 5 | TB6612_3 | A | Pin31 | Pin32 | Pin33 | Pin20 |

---

## 7. Notes

1. `Pin18` and `Pin19` are reserved for I2C.
2. `Pin10` is reserved for WS2812B output.
3. The current mapping assumes TB6612 STBY is tied high to 3.3V.
4. TB6612_3 B channel is spare for future expansion.