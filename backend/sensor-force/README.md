# Force Sensors with HX711
Load cells are available widely with the HX711 signal amplifier module as a package <<HX711LoadCellPackage>>. 
We will use one of these packages as the force measurement sensors.
The python module <<HX711PythonModule>> is slightly modified and contained in the backend sources.

## Hardware setup

### Prototype 11.01.2022
+ 2x load cell: https://www.amazon.de/gp/product/B088T78DNG/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1


### 4 load cell version

[#img-hx711]
.The HX711 with 4 load cells
image::./force/hx711_with_load_cells.jpg[{half-size}The HX711 with 4 load cells]
- HX711 analog-to-digital converter <<HX711Datasheet>>
- Load Cells

NOTE: Some HX711 modules have a wrong grounding according to the application sheet:
https://github.com/bogde/HX711/issues/172. This can be fixed with a small solder bridge.
[#img-hx711]
.The HX711 Fix
image::./force/hx711_fix.png[{half-size}The HX711 Fix]

Wire the HX711 module to the Raspberry Pi as follows:

[%header,cols="2,2,1"] 
|===
|Raspi GPIO
|Module
|Module Pin

|3v3
|HX711
|Vcc

|GPIO17
|HX711
|DT

|GPIO27
|HX711
|SCK

|===

Wire the 4 load cells as follows (according to the application sheet):

[#img-load-cell-wiring]
.Wiring four load cells
image::./force/4_load_sensors.jpg[{half-size}Wiring four load cells]

## Getting rid of the noise
As measured in <<<LPFvsKalman>>>: using a Low Pass Filter (moving average) is equivalent to a Kalman filter for HX711.

## Accuracy and limitations of the 50kg load cells:
- Ref: https://hackaday.io/project/182680-testing-out-50kg-load-cells


### Mounting the load sensors

#### Mounting the load cells in a zlagboard

. Disassemble the 4 screws and the gyroscope mount
. Place the 4 load cells at bottom 
. Create small "U-shaped" holds for the load cells (i.e. made from paper)

[#img-zlagboard-disassembled]
.Zlagboard disassembled
image::./force/zlagboard_disassemble.png[{half-size}Zlagboard disassembled]

[#img-zlagboard-load-cells]
.Zlagboard with load cells
image::./force/zlagboard_install_load_sensors.png[{half-size}Zlagboard with load cells]

[#img-zlagboard-ushaped-mount]
.U-Shaped load cell mount
image::./force/load_sensor_zlagboard_mount.png[{half-size}U-Shaped load cell mount]

NOTE: Gyroscope mount disabled after placing the load cells...


#### Mounting the load cells for any existing hangboard
Any hangboard can be mounted on a wooden construction with the 4 load cells in 
between. This will provice force measurements for any existing hangboard.

An example construction of a hangboard mount is given here: <<#img-mount-isometrix-board>>.

[#img-mount-isometrix-board]
.Mount for Isometrix Board <<ArduinoHangboard>>
image::./board_mount/IsometrixBoard.png[{half-size}Mount for Isometrix Board]



# How to configure the force sensor
+ Setup the hardware (mounting brackets, soldering HX711, wiring to raspi)
+ Calibrate the load cells


# Service: hanboard_sensor_force
## Installation
+ ``` make install ```

## Debugging
```
tail -f /var/log/sensor_force_std*
```

# API description:
- ./api/index.html
- Generate new API doc: `make api-doc`

# Debugging
- Check the events: `mosquitto_sub -h raspi-hangboard -t  hangboard/sensor/load/loadstatus`


# How to calibrate a load cell?
Prepare hangboard.ini:

referenceWeight1 = 5.
referenceValue1 = 238436.69
#referenceValue1 = 5

Configure the reference weight you want to use and set the reference value to the weight.
The is defined as: referenceUnit = referenceValue / referenceWeight

Run the sensor program:
`python3 ./sensor_force.py`

Put the weight on the load cell and observe "average load" converges to a value around the selected channel output:
```
SensorForce(MainThread) Both channels: -0.00 	 and 233394.67 yields: -0.00 	 and 0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.24 load 233394.66 load_bal -0.00 average load 234369.03 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 233103.67 yields: 0.00 	 and -0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.33 load 233394.66 load_bal -0.00 average load 234366.08 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 232992.67 yields: -0.00 	 and 0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.42 load 233103.66 load_bal -0.00 average load 234362.98 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 232745.67 yields: 0.00 	 and 0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.51 load 232992.66 load_bal -0.00 average load 234359.68 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 232697.67 yields: 0.00 	 and -0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.60 load 232745.66 load_bal -0.00 average load 234355.74 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 232645.67 yields: -0.00 	 and -0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.68 load 232697.66 load_bal -0.00 average load 234351.71 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 232969.67 yields: -0.00 	 and -0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.77 load 232645.66 load_bal -0.00 average load 234347.69 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 233205.67 yields: -0.00 	 and 0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.87 load 232969.66 load_bal -0.00 average load 234344.51 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 233681.67 yields: 0.00 	 and -0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328192.96 load 233205.66 load_bal -0.00 average load 234341.31 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
SensorForce(MainThread) Both channels: -0.00 	 and 234277.67 yields: -0.00 	 and 0.00 	 and 0.00
SensorForce(MainThread) Current time 1641328193.06 load 233681.66 load_bal -0.00 average load 234338.81 calculated FTI 0.00 maximal load 240428.66 RFD 32353.79 LoadLoss 0.03
```

Do this for both load sensors and insert the value (i.e. 234338.81) in the hangboard.ini file.


# References
* [[[HX711Datasheet]]] HX 711 Datasheet: https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/force/hx711_english.pdf
* [[[HX711LoadCellPackage]]] Package of HX711 module and 4 load cells: https://www.amazon.ca/Bridge-Digital-Amplifier-Arduino-DIYmalls/dp/B086ZHXNJH
* [[[HX711PythonModule]]] The python modules for HX711: https://github.com/tatobari/hx711py or https://github.com/gandalf15/HX711/