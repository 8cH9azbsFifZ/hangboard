# Gyroscope sensor

- Used: MPU-6050

# Developing
```
ssh -lpi raspi-hangboard
```

# Setup
## Wiring

Raspberry Pi	- MPU 6050
Pin 1 (3.3V)	- VCC
Pin 3 (SDA)	    - SDA
Pin 5 (SCL)	    - SCL
Pin 6 (GND)	    - GND

## Software
+ Enable I2C I/O using `sudo raspi-config`
+ Add the following modules to `/etc/modules`: `i2c-bcm2708` and `i2c-dev`
+ Install the I2C tools `sudo apt-get install i2c-tools `
+ Check whether 68 exists in `sudo i2cdetect -y 1`
```
python3 -m pip install -r requirements.txt
```

# References
+ Ref: https://github.com/rocheparadox/Kalman-Filter-Python-for-mpu6050
+ https://tutorials-raspberrypi.de/rotation-und-beschleunigung-mit-dem-raspberry-pi-messen/

## More possibilities?
- There is a bluetooth version, too: https://github.com/fundiZX48/pymotiontracker