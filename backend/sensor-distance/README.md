# Distance Sensor Service
** Status: to be re-integrated **

## Distance sensor HC-SR04
WARNING: This sensor is not yet fully implemented in the backend.

For measuring distances (i.e. for pullups) we will use a HC-SR04 ultrasonic distance sensor <<HCSR04Package>>.
There is excellent documentation on how to getting started <<HCSR04GettingStarted>>.
For accurate measurements a kalman filter is implemented in the backend based on <<HCSR04KalmanFilter>>.
More information also can be found in <<KalmanHCSR04>>.

Other alternatives are <<<VelocityBraincoder>>>.

[#img-sensor-hc-sr04]
.Sensor HC-SR04
image::./distance_sensors/doc/71YRg95095L._SL1500_.jpg[{half-size}Sensor HC-SR04]


Wire the distance sensor to the raspi as follows:

[%header,cols="2,2,1"] 
|===
|Raspi GPIO
|Module
|Module Pin

|Pin 2 (VCC)
| HC-SR04 
|VCC

|Pin 6 (GND)  
| HC-SR04 
|GND

|Pin 12 (GPIO18)
| HC-SR04 
|TRIG

|
| R1: 330Ω 
| ECHO 

| Pin 18 (GPIO24) 
| R1: 330Ω 
|          

|                 
| R1: 330Ω 
| R2: 10kΩ   

| Pin6 (GND)      
|          
|  R2: 10kΩ  

|===


# References
* [[[KalmanHCSR04]]]  Kalman Filter Algorithm Design for HC-SR04 Ultrasonic Sensor Data Acquisition System, Adnan Rafi Al Tahtawi https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/Kalman_Filter_Algorithm_Design_for_HC-SR04_Ultraso.pdf
* [[[HCSR04Package]]] HC-SR04 package: https://www.amazon.de/AZDelivery-HC-SR04-Ultraschall-Entfernungsmesser-Raspberry/dp/B07TKVPPHF/
* [[[HCSR04GettingStarted]]] Getting started with distance measurements using the HC-SR04: https://tutorials-raspberrypi.de/entfernung-messen-mit-ultraschallsensor-hc-sr04/
* [[[HCSR04KalmanFilter]]] Implementations of kalman filters for the HC-SR04 module: https://github.com/rizkymille/ultrasonic-hc-sr04-kalman-filter and https://github.com/NagarajSMurthy/Kalman-estimation-of-ultrasonic-sensor

* [[[VelocityBraincoder]]] Braincoder velocity sensor https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/Braincoder.pdf

