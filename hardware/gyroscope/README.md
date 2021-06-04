# Gyroscope sensor
![Sensore MPU-6050](./doc/SEN-MPU6050-01.png)
- Used: MPU-6050

# Developing
Running on raspi
```
ssh -lpi raspi-hangboard
cd hangboard/...
git pull
```
Or using docker
```
docker build . -t gyroscope
docker run --rm -it -p 4323:4323 gyroscope
```


## Debugging the websockets
wscat -c "ws://10.101.40.40:4323/"

# Setup 
## Wiring the Hardware
| Raspi GPIO   | Module   | Module Pin |
|--------------|----------|------------|
| Pin 1 (3.3V) | MPU 6050 | VCC        |
| Pin 3 (SDA)  | MPU 6050 | SDA        |
| Pin 5 (SCL)  | MPU 6050 | SCL        |
| Pin 6 (GND)  | MPU 6050 | GND        |


## Software
Enable I2C I/O, load user space module and install I2C tools
```
sudo sed -i 's/\#dtparam=i2c_arm=on/dtparam=i2c_arm=on/g' /boot/config.txt
grep i2c-dev /etc/modules ||echo i2c-dev |sudo tee -a /etc/modules
sudo apt-get -y install i2c-tools
```
+ Reboot
+ Check whether 68 exists in `sudo i2cdetect -y 1 | grep 68`
+ Install requirements 
```
python3 -m pip install -r requirements.txt
```

# References
+ Ref: https://github.com/rocheparadox/Kalman-Filter-Python-for-mpu6050
+ https://tutorials-raspberrypi.de/rotation-und-beschleunigung-mit-dem-raspberry-pi-messen/

## More possibilities?
- There is a bluetooth version, too: https://github.com/fundiZX48/pymotiontracker