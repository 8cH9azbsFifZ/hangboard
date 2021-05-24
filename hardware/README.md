# Hardware build
This directory contains the hardware build instructions.

# Force Sensors
- *Not implemented yet*
- HX711 analog-to-digital converter
- Load Cells

## HX711 Fix
![HX711 Fix](./force_sensors/hx711_fix.png)

## Raspi Wiring - HX711
3v3    - Vcc
GPIO17 - DT
GPIO27 - SCK
![Raspi GPIO](./raspi_w_gpio.jpg)


## HX711 Wiring - Load Cell
Red   - E+
Black - E-
White - A-
Green - A+

# Velocity Sensors
- *Not implemented yet*
- To build a linear encoder with the rotary encoder KY-040 you could follow the instructions of the [Braincoder](./velocity_sensors/linear_encoder/Braincoder.pdf).
- The pdf with the instructions (in spanish) the the 3d models are in `hardware/velocity_sensors/linear_encoder`.


## Raspi Wiring
![Raspi GPIO](./raspi_w_gpio.jpg)

