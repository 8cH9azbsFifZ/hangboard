# Wiring

Board Pin	Name	Anmerkung	Raspberry Pi Pin
1	VCC	+5V	Pin 2 (5V)
2	GND	Masse	Pin 6 (GND)
3	DIN	Daten Pin (in)	Pin 19 (GPIO10 / MOSI)
4	CS	Chip Select	Pin 24 (GPIO8 / CE0)
5	CLK	Clock	Pin 23 (GPIO11 / SCLK)
6	DOUT	Daten Pin (out)	nicht angeschlossen

# Installation

echo "Enable SPI"
sudo sed -i 's/\#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
sudo usermod -a -G spi,gpio pi
sudo apt-get -y install python-dev python-pip libfreetype6-dev libjpeg-dev
pip3 install luma.led_matrix

# References
- https://tutorials-raspberrypi.de/raspberry-pi-7-segment-anzeige-kathode-steuern/