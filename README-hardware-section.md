## Hardware Documentation

This repository includes a hardware architecture and implementation plan for a Teensy 4.1 based motorized mixer controller board.

### Main hardware features
- Teensy 4.1 main controller
- 5 motorized faders
- 3 TB6612 motor drivers
- 5 I2C OLED displays
- 1 TCA9548A I2C multiplexer
- 25 WS2812B RGB LEDs
- 2 HC4067 expansion multiplexers
- External 12V DC input
- On-board rails for:
  - 12V → 5V
  - 12V → 10V
  - 5V → 3.3V

### Documentation index
See [`docs/README.md`](docs/README.md) for the hardware documentation overview.

Key files:
- `docs/hardware-schematic-spec.md`
- `docs/pcb-layout-guide.md`
- `docs/pinout.md`
- `docs/fader-control.md`
- `docs/power-tree.md`
- `docs/bringup-checklist.md`
- `docs/net-naming-convention.md`

### Main design principles
- 12V is the external input rail
- 10V is used for motorized fader drive
- 5V is used for WS2812B LEDs
- 3.3V is used for MCU and logic
- OLED address conflicts are handled using TCA9548A
- Fader position sensing uses Teensy ADC inputs

### Current status
The repository documentation currently defines:
- hardware architecture
- rail generation and distribution
- motor driver mapping
- display bus structure
- LED chain design
- PCB layout rules
- bring-up process