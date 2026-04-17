# Firmware Interface Guide

## 1. Purpose

This document describes the hardware-facing firmware interface assumptions for the motorized mixer controller board.

It defines:
- power-related assumptions
- pin-level control groups
- display access model
- LED control model
- fader control model
- suggested firmware abstractions

This is not a complete firmware implementation document.
It is a hardware-to-firmware interface reference.

---

## 2. Main Firmware-Controlled Subsystems

The firmware interacts with these major blocks:

1. TCA9548A I2C multiplexer
2. 5 OLED displays
3. 25 WS2812B LEDs
4. 5 motorized faders
5. optional HC4067 devices
6. system-level power assumptions

---

## 3. Power Assumptions

Firmware assumes the following rails are already valid when the MCU is running:
- `+3V3_LOGIC`
- `+5V_LED`
- `+10V_MOTOR` if motor driving is expected

Firmware does not directly regulate these rails, but may infer faults from behavior:
- missing OLED response
- unstable ADC readings
- failed motor movement
- LED brownout behavior

---

## 4. I2C Interface Model

## 4.1 Main bus
Teensy I2C pins:
- `Pin18 = SDA`
- `Pin19 = SCL`

Devices on main bus:
- TCA9548A

Expected address:
- `0x70`

### Firmware requirement
Before talking to an OLED, firmware must:
1. select a TCA9548A channel
2. then communicate with the OLED on that selected channel

---

## 4.2 TCA9548A channel mapping

| Channel | Device |
|---|---|
| 0 | OLED1 |
| 1 | OLED2 |
| 2 | OLED3 |
| 3 | OLED4 |
| 4 | OLED5 |

Suggested firmware API concept:
- `selectDisplayChannel(index)`

---

## 5. OLED Interface Model

Each OLED is expected to behave like a standard I2C OLED module.

Likely assumptions:
- SSD1306-compatible
- same device address on each isolated channel

Suggested firmware abstraction:
- `displayInit(channel)`
- `displayClear(channel)`
- `displayDrawText(channel, x, y, text)`
- `displayUpdate(channel)`

Because the displays are multiplexed, all access should explicitly identify the channel.

---

## 6. WS2812B Interface Model

### 6.1 Data output
- `Pin10 = LED_DATA`

### 6.2 Topology
- one serial LED chain
- 25 LEDs total

Suggested firmware constants:
- `LED_COUNT = 25`
- `LED_DATA_PIN = 10`

Suggested firmware abstraction:
- `ledSet(index, r, g, b)`
- `ledFill(r, g, b)`
- `ledShow()`

### 6.3 Startup behavior
Recommended:
- initialize LEDs at low brightness first
- avoid instant full-white startup

---

## 7. Fader Interface Model

Each fader exposes:
1. one ADC input for position
2. one TB6612 motor control channel

---

## 7.1 Fader ADC mapping

| Fader | ADC pin |
|---|---|
| 1 | Pin14 (A0) |
| 2 | Pin15 (A1) |
| 3 | Pin16 (A2) |
| 4 | Pin17 (A3) |
| 5 | Pin20 (A6) |

Suggested firmware abstraction:
- `readFaderRaw(index)`
- `readFaderNormalized(index)`

Normalized output may be scaled to:
- `0.0 ... 1.0`
or
- `0 ... 1023`
depending on firmware style

---

## 7.2 Fader motor mapping

| Fader | Driver | PWM | IN1 | IN2 |
|---|---|---|---|---|
| 1 | TB6612_1A | Pin23 | Pin41 | Pin40 |
| 2 | TB6612_1B | Pin22 | Pin38 | Pin39 |
| 3 | TB6612_2A | Pin21 | Pin37 | Pin36 |
| 4 | TB6612_2B | Pin13 | Pin35 | Pin34 |
| 5 | TB6612_3A | Pin31 | Pin32 | Pin33 |

Suggested firmware abstraction:
- `faderMotorForward(index, pwm)`
- `faderMotorReverse(index, pwm)`
- `faderMotorBrake(index)`
- `faderMotorStop(index)`

---

## 8. Fader Closed-Loop Control Concept

Recommended control flow per fader:

1. read target position
2. read current ADC position
3. compute error
4. if error is inside deadband:
   - stop or brake
5. else:
   - choose direction
   - apply PWM proportional to error magnitude

Suggested higher-level API:
- `setFaderTarget(index, target)`
- `updateFaderControl(index)`

---

## 9. Fader Safety Suggestions

Firmware should include:

### 9.1 Deadband
Prevents oscillation near target.

### 9.2 Maximum PWM limit
Avoids harsh motion and excess current.

### 9.3 Slew or soft approach
Reduce PWM near final target.

### 9.4 Timeout / stall protection
If ADC position does not change while motor is driven, stop and flag error.

### 9.5 Startup calibration strategy
Optional:
- read current position on boot
- initialize software state without moving immediately

---

## 10. Suggested Firmware Data Structures

Example conceptual structure:

```text
FaderState:
  adcPin
  pwmPin
  in1Pin
  in2Pin
  rawValue
  filteredValue
  targetValue
  error
  enabled
```

For displays:

```text
DisplayState:
  tcaChannel
  initialized
  address
```

For LEDs:

```text
LedState:
  count = 25
  brightness
```

---

## 11. Suggested Initialization Order

1. initialize serial/debug output
2. initialize GPIO directions
3. initialize I2C
4. initialize TCA9548A
5. initialize OLEDs one by one by channel
6. initialize LED library
7. initialize ADC
8. initialize fader control state
9. run low-risk hardware self-checks

---

## 12. Suggested Runtime Update Loop

Possible loop structure:

1. read inputs
2. read fader ADC values
3. update target positions
4. update fader motor control
5. update OLED content if needed
6. update LED state
7. run diagnostics / fault checks

---

## 13. Fault Conditions Worth Detecting

Firmware may detect or infer:
- TCA9548A not responding
- OLED not responding on a channel
- ADC value stuck or out of range
- motor commanded but no motion observed
- position unstable beyond expected noise
- supply-related symptoms such as resets or display dropouts

---

## 14. Notes

1. TB6612 STBY is assumed tied high in hardware.
2. The spare TB6612 channel is currently unused.
3. All logic signaling is assumed 3.3V-domain compatible.
4. OLED selection always requires TCA channel selection first.
5. Fader control should be treated as closed-loop, not open-loop timed movement.