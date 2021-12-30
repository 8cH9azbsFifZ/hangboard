
# Force Sensors with HX711
Load cells are available widely with the HX711 signal amplifier module as a package <<HX711LoadCellPackage>>. 
We will use one of these packages as the force measurement sensors.
The python module <<HX711PythonModule>> is slightly modified and contained in the backend sources.

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




## Mounting the load sensors

### Mounting the load cells in a zlagboard

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


### Mounting the load cells for any existing hangboard
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
```
./install_hangboard_sensor_force.sh
```

## Debugging
```
tail -f /var/log/sensor_force_std*
```
