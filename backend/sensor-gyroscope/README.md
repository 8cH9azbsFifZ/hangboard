# Gyroscope Sensor Service

** Status: to be re-integrated **


## Gyroscope Sensor: MPU-6050
Without further modifications a gyroscoope sensor can be mounted on an existing Zlagboard.
Hangs can be measured with the gyroscope, too. We will use the widely used MPU6050 package 
<<MPU6050Datasheet>> with excellent documentations <<MPU6050GettingStarted>>. 
Obviously there will be noise in the measurements, so for accurate 
measurements in our setup a kalman filter is implemented in the backend, based on this implementation
<<MPU6050KalmanFilter>>.

CAUTION: Force measurements are not possible without the load cells.

NOTE: Modules with BLE are existing for further / future developments <<MPU6050BLEVersion>>.

[#img-sensor-mpu-6050]
.Sensor MPU-6050
image::./gyroscope/SEN-MPU6050-01.png[{half-size}Sensor MPU-6050]

Wire the Gyroscope sensor to the raspi as follows:

[%header,cols="2,2,1"] 
|===
|Raspi GPIO
|Module
|Module Pin

|Pin 1 (3.3V)
| MPU 6050
|VCC

|Pin 3 (SDA
| MPU 6050
|SDA

|Pin 5 (SCL)
| MPU 6050
|SCL

| Pin 6 (GND)
| MPU 6050
|GND

|===


For getting started with the software for the Gyroscope, follow these steps

. Enable I2C I/O `sudo sed -i 's/\#dtparam=i2c_arm=on/dtparam=i2c_arm=on/g' /boot/config.txt`
. Load the user space module `grep i2c-dev /etc/modules ||echo i2c-dev |sudo tee -a /etc/modules`
. Install I2C tools `sudo apt-get -y install i2c-tools`
. Reboot `sudo reboot`
. Check whether 68 exists in `sudo i2cdetect -y 1 | grep 68`

