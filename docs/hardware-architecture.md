# Hardware Architecture

## Project Overview
This documentation outlines the complete hardware architecture and development reference for the mixer controller simulator project.

## System Functional Blocks
- Project overview
- System components and their interactions.

## Teensy 4.1 Responsibilities
- Coordinate the functionalities of the faders.
- Manage motor driver communications.
- Handle ADC position sensing for faders.

## Motorized Fader Details for RSA0N11M9A0J
- **10V Motor Requirement:**
  - The motor operates at a 10V supply.
- **ADC Position Sensing:**
  - The fader positions are monitored through an ADC.

## 3 TB6612 Motor Driver Architecture
- **Mapping for 5 Faders:**
  - Each fader is assigned a dedicated TB6612 channel for control.

## Complete Power Architecture
- **12V Input** 
- **Switch**
- **12V Bus**
- **MP2315 12V-to-5V Rail**
- **AMS1117 5V-to-3.3V Rail**
- **MP2315 12V-to-10V Rail**

## MP2315 Pin Mapping
- **Pin1:** AAM
- **Pin2:** IN
- **Pin3:** SW
- **Pin4:** GND
- **Pin5:** BST
- **Pin6:** EN
- **Pin7:** VCC
- **Pin8:** FB

## Detailed 12V-to-5V and 12V-to-10V Wiring Summaries
- *Feedback Resistor Values:* (specific values to be included based on design)

## TB6612 Power Connections
- Recommended power connection schemes with local decoupling recommendations.

## Full Teensy Pin Allocation for Motor Channels
- Details on how pins are assigned for motor channel operations.

## Detailed Fader Position Sensing ADC Mapping
- Complete description of ADC channels used for position sensing.

## TCA9548A Architecture
- Descriptions of the TCA9548A multiplexer configuration and OLED channel mapping.

## WS2812B Architecture
- **LED Control:** Pin10 through 330-ohm resistor to LED1 DIN in a daisy chain of 25 LEDs.

## Capacitor Guidance
- Use of capacitors: 100uF and 100nF parallel decoupling.

## Known Confirmed Capacitor Part Numbers
- HGC1206R5107M100NSPJ
- CGA0603X7R104K500JT

## Current Confirmed Teensy Pin Usage
- A detailed inventory of Teensy pins being used in the design.

## Design Constraints and Notes
- Any limitations or considerations in the design process.

## Suggested Future Documentation Files
- Listing potential additional documentation that may be required in the future.

## Suggested Next Tasks
- Outline of tasks to proceed with the development process.