# Wiring

Board Pin	Name	Anmerkung	Raspberry Pi Pin
1	VCC	+5V	Pin 2 (5V)
2	GND	Masse	Pin 6 (GND)
3	DIN	Daten Pin (in)	Pin 19 (GPIO10 / MOSI)
4	CS	Chip Select	Pin 24 (GPIO8 / CE0)
5	CLK	Clock	Pin 23 (GPIO11 / SCLK)
6	DOUT	Daten Pin (out)	nicht angeschlossen

# Installation
+ `make prepare`
+ `make install`


# References
- https://tutorials-raspberrypi.de/raspberry-pi-7-segment-anzeige-kathode-steuern/