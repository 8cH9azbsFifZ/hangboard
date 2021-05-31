# Force Sensors
- *Not implemented yet*
- HX711 analog-to-digital converter
- Load Cells

# Software
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

# Hardware Setup

## HX711 Fix
![HX711 Fix](./doc/hx711_fix.png)

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

### Wiring two cells
HX711.E+ - Cell1.White + Cell2.Black
HX711.E- - Cell1.Black + Cell2.White
HX711.A+ - Cell1.Red
Hx711.A- - Cell2.Red

# References
+ https://www.amazon.ca/Bridge-Digital-Amplifier-Arduino-DIYmalls/dp/B086ZHXNJH
+ https://arduino.stackexchange.com/questions/17542/connect-hx711-to-a-three-wire-load-cell
+ https://github.com/tatobari/hx711py
