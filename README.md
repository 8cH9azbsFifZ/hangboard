# Hangboard 
*A universal force and velocity sensing hangboard mount with exercise timers for all hangboards.*

## Current Status
*STATUS: In Development - Towards a reproduceable prototype*
+ [Bugs](https://github.com/8cH9azbsFifZ/hangboard/labels/bug)
+ [Features TBD](https://github.com/8cH9azbsFifZ/hangboard/labels/feature)


## TESTING
"...the **go to** statement should be abolished..." [[1]](#Website).






# Why a universal smart hangboard?
Nowadays smart hangboards are becoming more and more popular. And there is a growing market for commercial
products (they are expensive): <<BeastMakerMotherboard>>, <<Climbro>>, <<SmartBoard>>, <<Entralpi>>
All existing hangboard training apps have limitations (i.e. payed subscriptions,
limited to specific hangboards, buggy, sketchy to create new or custom training plans). In the recent years
there have been a couple of attempts to create hombrew smart hangboards (i.e. <<PiClimbing>> and <<ArduinoHangboard>>).

This was motivation for me to learn new technologies and build an own smart hangboard - which is easy to reproduce for others.

[#img-smart-hangboard]
.Smart Hangboard
image::./board_mount/smart_hangboard_v2.png[{half-size}Smart Hangboard]

# What you need

- Any hangboard (large list of supported hangboards below).
- A Raspberry Pi, force sensors and some basic skills to setup the software backend (no automation so far).
- Basic skills to create a board mount with the force sensors.
- Any mobile device (iOS / Android / WebApp) and some basic skills to deploy the debugging app (no Store so far)

TIP: Further information can be found in the repository: https://github.com/8cH9azbsFifZ/hangboard.

# Features
- Smart exercise timer - easily customizeable
- Uses preexisting exercise files - easily extendable
- Measures hangtime, applied force, rate-of-force development, maximal load 

[#img-smart-hangboard-app]
.Smart Hangboard App
image::./app/app_screenshot.png[{half-size}Smart Hangboard App]


# Software Design
This is a brief design layout of the project. 

## Frontend
- Web client (Running on the backend Raspberry Pi)
- iOS App
- Android App 

## Backend
- Running on a Raspberry Pi.
- Communicating to the frontend using MQTT.
- The default hostname for the MQTT broker is "hangboard". Modification is possible in backend and frontend with a variable so far.

The class documentation of the backend services can be found here: https://8ch9azbsfifz.github.io/hangboard/backend-doc/index.html.

## Software Used
- Flutter for the frontends
- Python backends
- MQTT for Communication 
- JSON for Board configuration and finger grip positions
- SVG Layers for hold configuration (will be converted to PNG in a cache, as flutter has no native SVG support)
- REST api for image and sound sources

### Software documentation
- For manual documentation (manual creation): install `brew install asciidoctor` and create the PDF `cd doc; asciidoctor-pdf Manual.adoc`
- Documentation of the backend software can be created using `doxygen` (cf. Doxyfile). `brew install doxygen`.
- The documentation is automatically generated using a commit hook on github and published on gh-pages.

#### API (MQTT)
The documentation of the backend API can be found here: https://8ch9azbsfifz.github.io/hangboard/api/index.html .

- AsyncAPI for documentation of the API
- For manual generation install ```npm install -g @asyncapi/generator ``` and run ```cd backend ; ag asyncapi.yaml @asyncapi/html-template -o ./docs```
- If you want to run MQTT locally on the raspi run `sudo apt-get -y install mosquitto`


# Hardware Design
- Raspberry Pi Zero W
- Sensors: as listed below

All sensors can be wired at once following this schema:
[#img-hangboard-wiring]
.Hangboard wiring - all sensors
image::./hardware/hangboard_wiring.png[{half-size}Hangboard wiring - all sensors]





# Measurements, their definitions and what to learn from them
The following values are measured. For more informations on their meaning refer to the papers given in the references.
*TODO*

MVC:: Maximum Voluntary Contraction *TODO*

RFD:: Rate of force development (N/s) *TODO*

FTI:: Force-Time-Integral *TODO*

Average Load:: *TODO*

Maximal Load:: *TODO*

Load Loss:: *TODO*

Load:: *TODO*


## Evaluations of the measured data

From the MVC we can estimate the maximal boulder grade according to [[[MVC1]]] using 
the script in `evaluations/estimate_bouldergrade_from_mvc.py`.

Here are some first test measurement data sets. The test has been conducted with a hang, one handed pulls, a fast and a slow pullup.
The data and evaluation scripts can be found in the directory `evaluations`.

[#img-measurement-test1-load]
.Measurement of Load (Test 1)
image::app/Load.png[{half-size}Measurement of Load (Test 1)]

[#img-measurement-test1-loadavg]
.Measurement of average Load (Test 1)
image::app/LoadAvg.png[{half-size}Measurement of average Load (Test 1)]

[#img-measurement-test1-loadmax]
.Measurement of maximal Load (Test 1)
image::app/LoadMax.png[{half-size}Measurement of maximal Load (Test 1)]

[#img-measurement-test1-loadloss]
.Measurement of Load Loss (Test 1)
image::app/LoadLoss.png[{half-size}Measurement of Load loss (Test 1)]

[#img-measurement-test1-fti]
.Measurement of FTI (Test 1)
image::app/FTI.png[{half-size}Measurement of FTI (Test 1)]

[#img-measurement-test1-rfd]
.Measurement of RFD (Test 1)
image::app/RFD.png[{half-size}Measurement of RFD (Test 1)]



# References
<a id="Website">[1]</a> Hangboard website: https://8ch9azbsfifz.github.io/hangboard/
<a id="2">[2]</a> Dijkstra, E. W. (1968). Go to statement considered harmful. Communications of the ACM, 11(3), 147-148.


* [[[]]] 
* [[[Discussions]]] Hangboard discussions: https://github.com/8cH9azbsFifZ/hangboard/discussions
* [[[Issues]]] Hangboard issues: https://github.com/8cH9azbsFifZ/hangboard/issues
* [[[PiClimbing]]] Raspi W Zero Hangboard: https://github.com/adrianlzt/piclimbing
* [[[ArduinoHangboard]]] Arduino Hangboard: https://github.com/oalam/isometryx
* [[[HX711Datasheet]]] HX 711 Datasheet: https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/force/hx711_english.pdf
* [[[HX711LoadCellPackage]]] Package of HX711 module and 4 load cells: https://www.amazon.ca/Bridge-Digital-Amplifier-Arduino-DIYmalls/dp/B086ZHXNJH
* [[[HX711PythonModule]]] The python modules for HX711: https://github.com/tatobari/hx711py or https://github.com/gandalf15/HX711/
* [[[MPU6050Datasheet]]] MPU 6050 Datasheet: https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/gyroscope/MPU-6000-Register-Map1.pdf
* [[[MPU6050KalmanFilter]]] Kalman filter implementation for MPU 6050: https://github.com/rocheparadox/Kalman-Filter-Python-for-mpu6050
* [[[MPU6050GettingStarted]]] Getting started with MPU6050 measurements: https://tutorials-raspberrypi.de/rotation-und-beschleunigung-mit-dem-raspberry-pi-messen/
* [[[MPU6050BLEVersion]]] MPU6050 BLE module: https://github.com/fundiZX48/pymotiontracker
* [[[HCSR04Package]]] HC-SR04 package: https://www.amazon.de/AZDelivery-HC-SR04-Ultraschall-Entfernungsmesser-Raspberry/dp/B07TKVPPHF/
* [[[HCSR04GettingStarted]]] Getting started with distance measurements using the HC-SR04: https://tutorials-raspberrypi.de/entfernung-messen-mit-ultraschallsensor-hc-sr04/
* [[[HCSR04KalmanFilter]]] Implementations of kalman filters for the HC-SR04 module: https://github.com/rizkymille/ultrasonic-hc-sr04-kalman-filter and https://github.com/NagarajSMurthy/Kalman-estimation-of-ultrasonic-sensor
* [[[Beastmaker1000HoldSizes]]] Accurate measurements of the Beastmaker 1000 hold dimensions: https://rupertgatterbauer.com/beastmaker-1000/#:~:text=Speaking%20of%20design%2C%20the%20Beasmaker,slopers%20and%20pull%2Dup%20jugs.
* [[[Boards]]] Project with lots of hangboard configurations: https://github.com/gitaaron/boards
* [[[ClimbHarderSurvey]]] https://www.reddit.com/r/climbharder/comments/6693ua/climbharder_survey_results/ and the data stored here `doc/references/ClimbHarderSurvey`
* [[[CriticalForceCalculator]]] https://strengthclimbing.com/critical-force-calculator/
* [[[ClimbingFingerStrengthAnalyzer]]] https://strengthclimbing.com/finger-strength-analyzer/
* [[[ForceSensingHangboardToEnhangeFingerTraining]]] Force-Sensing Hangboad to Enhance Finger Training in Rock Climbers, M. Anderson (https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/Force-Sensing_Hangboard_to_Enhance_Finger_Training_in_Rock_Climbers.pdf)
* [[[VelocityBraincoder]]] Braincoder velocity sensor https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/Braincoder.pdf
* [[[MVC1]]] Optimizing Muscular Strength-to-Weight Ratios in Rock Climbing, https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/BF_strength_climbing_correlations-MAR282018web.pdf
* [[[LPFvsKalman]]] Simple Effective and Robust Weight Sensor for Measuring Moisture Content in Food Drying Process, https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/SM1941.pdf
* [[[MVC2]]] Tendinous Tissue Adaptation to Explosive- vs. Sustained-Contraction Strength Training, https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/fphys-09-01170.pdf
* [[[KalmanHCSR04]]]  Kalman Filter Algorithm Design for HC-SR04 Ultrasonic Sensor Data Acquisition System, Adnan Rafi Al Tahtawi https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/Kalman_Filter_Algorithm_Design_for_HC-SR04_Ultraso.pdf
* [[[LatticeMVC]]] The determination of finger flexor critical force in rock climbers https://github.com/8cH9azbsFifZ/hangboard/raw/main/doc/references/Giles2019Thedeterminationoffingerflexorcriticalforceinrockclimbers.pdf
* [[[BeastMakerMotherboard]]] Force sensing motherboard for beastmaker https://www.beastmaker.co.uk/products/motherboard
* [[[Climbro]]] Force sensing smart hangboard https://climbro.com/
* [[[SmartBoard]]] Force sesing smart hangboard https://www.smartboard-climbing.com/
* [[[Entralpi]]] Force sensing plate for smart hangboard training https://entralpi.com/
* [[[SmartRock]]] Universal mount for hangboards in door frames https://smartrock.de/?lang=de
* [[[Pull-Up Pocket Sensor]]] Pull-up Sensor and Counter - Arduino Nano 33 BLE - tinyML https://create.arduino.cc/projecthub/tl9672/pull-up-sensor-and-counter-arduino-nano-33-ble-tinyml-6516d2


