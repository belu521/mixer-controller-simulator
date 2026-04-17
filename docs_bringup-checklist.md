# Bring-Up Checklist

## 1. Purpose

This document provides a structured hardware bring-up flow for the motorized mixer controller board.

The goal is to reduce risk during first power-up and early testing.

---

## 2. Before Applying Power

## 2.1 Visual inspection
- [ ] Confirm component orientation for all ICs
- [ ] Confirm polarity of all polarized capacitors
- [ ] Confirm Schottky diode orientation on both MP2315 supplies
- [ ] Confirm AMS1117 orientation
- [ ] Confirm TB6612 orientation
- [ ] Confirm no missing decoupling capacitors
- [ ] Confirm no obvious solder bridges

## 2.2 Continuity checks
With power disconnected:
- [ ] Check `+12V_IN` is not shorted to GND
- [ ] Check `+12V_SW` is not shorted to GND
- [ ] Check `+5V_LED` is not shorted to GND
- [ ] Check `+3V3_LOGIC` is not shorted to GND
- [ ] Check `+10V_MOTOR` is not shorted to GND

## 2.3 Power path confirmation
- [ ] Confirm DC jack Pin1 goes to switch COM
- [ ] Confirm switch NO goes to `+12V_SW`
- [ ] Confirm DC jack Pin2 goes to GND

---

## 3. Stage 1: Input Power Test

Apply external 12V with no sensitive modules attached if possible.

- [ ] Measure DC jack input voltage
- [ ] Toggle switch and confirm `+12V_SW` appears correctly
- [ ] Confirm switch operation is stable
- [ ] Confirm no unexpected heating

If failure occurs:
- stop immediately
- inspect input path, switch wiring, and shorts

---

## 4. Stage 2: 5V Buck Test

Before connecting LED loads:

- [ ] Measure MP2315 #1 output
- [ ] Confirm output is approximately 4.8V to 5V
- [ ] Confirm no large ripple or unstable oscillation
- [ ] Confirm inductor and diode are not overheating

If output is incorrect:
- inspect feedback divider
- inspect BST capacitor
- inspect diode orientation
- inspect inductor connection
- inspect EN/IN/VCC wiring

---

## 5. Stage 3: 10V Buck Test

Before connecting motor loads:

- [ ] Measure MP2315 #2 output
- [ ] Confirm output is approximately 10V to 10.6V
- [ ] Confirm output is stable
- [ ] Confirm inductor does not overheat
- [ ] Confirm diode orientation is correct

If output is incorrect:
- inspect feedback divider
- inspect diode polarity
- inspect SW to inductor path
- inspect GND return
- inspect EN/IN/VCC wiring

---

## 6. Stage 4: 3.3V Regulator Test

With 5V rail stable:

- [ ] Measure AMS1117 output
- [ ] Confirm `+3V3_LOGIC` is approximately 3.3V
- [ ] Confirm regulator is not overheating
- [ ] Confirm 3.3V is stable under light load

If incorrect:
- inspect regulator orientation
- inspect input/output caps
- inspect 5V input availability
- inspect shorts on 3.3V rail

---

## 7. Stage 5: Logic Power Validation

Before testing firmware:

- [ ] Confirm Teensy power pins receive valid logic supply
- [ ] Confirm TCA9548A VCC is 3.3V
- [ ] Confirm OLED VCC rails are 3.3V
- [ ] Confirm TB6612 VCC is 3.3V
- [ ] Confirm TB6612 STBY is high (3.3V)

---

## 8. Stage 6: I2C Validation

With Teensy firmware loaded for I2C scan:

- [ ] Confirm TCA9548A responds at address `0x70`
- [ ] Confirm SDA and SCL pull-ups are present
- [ ] Confirm no bus lockup
- [ ] Select each TCA channel and test OLED presence
- [ ] Confirm each OLED works independently

If issues occur:
- inspect SDA/SCL routing
- inspect pull-up resistors
- inspect TCA address pins
- inspect OLED power and ground

---

## 9. Stage 7: WS2812B Validation

Before full-brightness testing:

- [ ] Confirm LED1 DIN is connected through 330Ω resistor
- [ ] Confirm 5V rail is present near LED chain
- [ ] Confirm GND continuity along LED chain
- [ ] Run a simple test pattern at low brightness first
- [ ] Confirm data propagates through chain

If issues occur:
- inspect DIN/DOUT order
- inspect 5V/GND polarity
- inspect soldering on first LED
- inspect common ground with Teensy

---

## 10. Stage 8: ADC / Fader Position Validation

Without motor movement first:

- [ ] Confirm each fader potentiometer high end is 3.3V
- [ ] Confirm each low end is GND
- [ ] Confirm each wiper reaches the correct ADC pin
- [ ] Read raw ADC values while moving each fader manually
- [ ] Confirm values change smoothly over travel

If issues occur:
- inspect wiper routing
- inspect reference ends
- inspect ADC filtering network if fitted
- inspect for noisy routing near motor area

---

## 11. Stage 9: TB6612 Idle Validation

Before driving motors:

- [ ] Confirm VM = about 10V
- [ ] Confirm VCC = 3.3V
- [ ] Confirm STBY = 3.3V
- [ ] Confirm no TB6612 overheating at idle
- [ ] Confirm motor outputs are not shorted

---

## 12. Stage 10: Single Fader Motor Test

Test one motor first.

- [ ] Enable one TB6612 channel only
- [ ] Apply low PWM
- [ ] Confirm motor moves in one direction
- [ ] Reverse direction and confirm opposite movement
- [ ] Confirm motor does not stall excessively
- [ ] Confirm TB6612 remains within safe temperature

If direction is reversed:
- swap motor wires
or
- invert firmware logic

---

## 13. Stage 11: Closed-Loop Fader Test

After position sensing and motor drive both work:

- [ ] Read target position
- [ ] Read actual ADC value
- [ ] Drive toward target using low PWM first
- [ ] Confirm movement stops near target
- [ ] Add deadband to reduce hunting
- [ ] Tune PWM limits and approach behavior

---

## 14. Stage 12: Multi-Fader Test

- [ ] Test 2 faders simultaneously
- [ ] Test all 5 faders at low speed
- [ ] Observe 10V rail stability
- [ ] Observe 3.3V rail noise or reset issues
- [ ] Observe thermal behavior of TB6612 and 10V power stage

---

## 15. Recommended Bring-Up Order Summary

1. Visual inspection
2. Rail short check
3. Input 12V test
4. 5V buck test
5. 10V buck test
6. 3.3V regulator test
7. Logic rail validation
8. I2C and OLED test
9. WS2812B test
10. ADC fader test
11. TB6612 idle test
12. single motor test
13. closed-loop test
14. full-system test

---

## 16. Common Failure Sources

1. MP2315 feedback resistor wrong value
2. Schottky diode reversed
3. inductor disconnected or wrong value
4. TCA9548A address or pull-up issue
5. OLED wired to wrong channel
6. WS2812B DIN/DOUT reversed
7. ADC wiper connected to wrong pin
8. TB6612 VM missing
9. motor wires swapped
10. noisy analog routing causing unstable fader control