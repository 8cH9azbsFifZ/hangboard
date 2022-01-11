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
<a id="PiClimbing">[1]</a> Raspi W Zero Hangboard: https://github.com/adrianlzt/piclimbing<br/>
<a id="ArduinoHangboard">[2]</a> Arduino Hangboard: https://github.com/oalam/isometryx
<a id="BeastMakerMotherboard">[3]</a>Force sensing motherboard for beastmaker https://www.beastmaker.co.uk/products/motherboard
<a id="Climbro">[4]</a>Force sensing smart hangboard https://climbro.com/
<a id="SmartBoard">[5]</a> Force sesing smart hangboard https://www.smartboard-climbing.com/
<a id="Entralpi">[6]</a>Force sensing plate for smart hangboard training https://entralpi.com/
<a id="ArduinoHangSmartRockboard">[7]</a>Universal mount for hangboards in door frames https://smartrock.de/?lang=de
