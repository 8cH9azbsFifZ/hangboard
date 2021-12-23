Service for running a 


# Installation
```
apt-get install python-smbus i2c-tools
```
... both exist?

## I2C enable
```
sudo raspi-config nonint do_i2c 0
```
Ref: https://pi3g.com/de/2021/05/20/enabling-and-checking-i2c-on-the-raspberry-pi-using-the-command-line-for-your-own-scripts/



sudo i2cdetect -y 1


Falls du hier eine andere Zahl als 27 angezeigt bekommst, musst du dies gleich in der lcddriver.py Datei ändern (ADDRESS = 0x27).

# Library
 python3 -m pip install RPLCD
 



# References 
- https://tutorials-raspberrypi.de/hd44780-lcd-display-per-i2c-mit-dem-raspberry-pi-ansteuern/
