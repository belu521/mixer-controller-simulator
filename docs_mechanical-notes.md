# Mechanical Notes

## 1. Purpose

This document records the mechanical and physical integration considerations for the motorized mixer controller board.

It is intended for:
- PCB size planning
- front-panel alignment
- connector placement
- module mounting decisions
- enclosure integration
- future revision planning

This is not a final mechanical drawing.
It is a design guidance document.

---

## 2. System Mechanical Overview

The board is intended to support a mixer-style control surface with:
- 5 motorized faders
- 5 OLED displays
- 25 WS2812B indicator LEDs
- Teensy 4.1 control electronics
- power input and switching hardware

The likely final physical layout is long and panel-oriented rather than compact-square.

---

## 3. Primary Mechanical Elements

### 3.1 Motorized faders
Part:
- RSA0N11M9A0J

Mechanical considerations:
- 100 mm travel
- slider shaft must align accurately with panel slot
- mounting holes and body placement must match manufacturer drawing
- adequate clearance needed for fader body depth and cable/terminal access

### 3.2 OLED displays
Each OLED must align with the user-visible panel opening or viewing area.

Mechanical considerations:
- connector orientation
- viewing angle
- spacing relative to fader or channel strip
- standoff or header height if module-mounted

### 3.3 WS2812B LEDs
LED placement depends on front panel visual design.

Mechanical considerations:
- light pipe or diffuser usage
- spacing regularity
- visibility angle
- thermal clustering if densely packed

### 3.4 Teensy 4.1
Mechanical considerations:
- USB access if needed
- service access after assembly
- socketed vs soldered mounting choice
- keep clear of moving or panel-critical elements

---

## 4. Suggested Mechanical Layout Strategy

A mixer-style channel-strip layout is recommended.

For each channel strip, likely vertical arrangement:
1. OLED display
2. status LEDs
3. encoder / buttons if present
4. motorized fader

Across the board:
- 5 repeated channel strips
- shared power and control electronics grouped in a less visible area if possible

---

## 5. Suggested PCB Shape Considerations

Because the board includes multiple faders and displays, likely options are:

### Option A: One long main board
Advantages:
- fewer interconnects
- simpler grounding
- single assembly

Disadvantages:
- larger PCB cost
- more difficult panel alignment across full length
- more mechanical stress risk

### Option B: Main board plus smaller front-panel modules
Advantages:
- modular channel design
- easier mechanical repetition
- potentially easier panel alignment

Disadvantages:
- more connectors
- more wiring complexity
- more assembly complexity

At the current documentation stage, the design assumes:
- one integrated board or one highly coordinated layout plan

---

## 6. Panel Alignment Notes

### 6.1 Fader alignment
- fader slot position must match the mechanical drawing exactly
- allow tolerance for knob cap width and slot travel clearance
- verify end-stop clearance against panel slot length

### 6.2 OLED alignment
- OLED active area should be centered in panel window
- avoid placing module edges where they interfere with the panel opening
- account for bezel or diffuser if used

### 6.3 LED alignment
- if LEDs are panel indicators, ensure center-to-center spacing is visually consistent
- decide early whether LEDs are direct-view, under-diffuser, or light-pipe coupled

---

## 7. Mounting and Support

Recommended:
- define mounting holes early
- place board mounting holes away from fader body and display apertures
- avoid routing critical traces too close to mounting holes
- ensure the board is supported to avoid flexing during fader operation

Because motorized faders are actuated parts, PCB stiffness matters.

---

## 8. Connector and Service Access

### 8.1 Power input
- place DC jack in an enclosure-accessible location

### 8.2 USB or programming access
- if Teensy USB is needed after assembly, keep a clear access path

### 8.3 Debug access
- test points or debug header should remain accessible if practical

---

## 9. Height and Clearance Considerations

Check the following early:
- fader body depth under PCB
- OLED module thickness above PCB
- header height for module connections
- switch and DC jack panel clearance
- nearby enclosure lid clearance
- standoff height and screw head interference

---

## 10. Thermal and Mechanical Interaction

Main thermal sources:
- buck converters
- TB6612 motor drivers
- LED clusters at high brightness

Mechanical impact:
- avoid placing heat-generating devices directly under heat-sensitive displays or close to hand-contact surfaces
- allow copper area for spreading heat

---

## 11. Recommended Early Mechanical Validation Tasks

1. import fader mechanical drawing into PCB CAD as reference
2. define panel cutout positions first
3. place OLED view areas relative to panel openings
4. place mounting holes early
5. confirm connector accessibility
6. confirm no collision between tall parts and enclosure

---

## 12. Notes

1. The fader mechanical drawing should be treated as a primary constraint.
2. Visual symmetry is important for mixer-style products.
3. Mechanical serviceability should be considered before finalizing Teensy and connector placement.
4. PCB stiffness matters because faders are user-actuated mechanical parts.