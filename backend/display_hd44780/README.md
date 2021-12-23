Service for running a 


# Installation
```
apt-get install python-smbus i2c-tools
```

## I2C enable
sudo raspi-config

Unter „8. Advanced Options“ > „A7 I2C“ aktivieren wir es. Nun fügen wir der modules-Datei noch die entsprechenden Einträge hinzu:


sudo nano /etc/modules
i2c-bcm2708
i2c-dev


sudo i2cdetect -y 1


Falls du hier eine andere Zahl als 27 angezeigt bekommst, musst du dies gleich in der lcddriver.py Datei ändern (ADDRESS = 0x27).





# References 
- https://tutorials-raspberrypi.de/hd44780-lcd-display-per-i2c-mit-dem-raspberry-pi-ansteuern/
