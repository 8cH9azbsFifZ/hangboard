# Hangboard 

*STATUS: In Development*

A universal force and velocity sensing hangboard mount with exercise timers for all hangboards.
![Hangboard Mount](./hardware/board_mount/IsometrixBoard.png)

Website: https://8ch9azbsfifz.github.io/hangboard/
Discussions: https://github.com/8cH9azbsFifZ/hangboard/discussions
Issues: https://github.com/8cH9azbsFifZ/hangboard/issues

# Developing

## Preparation
+ Follow the instructions in README.md in exercises and hangboard-app

## Running the Demonstrator
+ Start Exercises `cd exercises && ./startup.sh`
+ Start the Web App: `cd hangboard-web && ./startup.sh`
+ Start the iOS App: `cd hangboardapp && yarn run ios`

## Software Used
- Python Flask for Web App
- Websockets for Communication
- Python backends
- JSON for Board configuration and finger grip positions
- SVG Layers for hold configuration
- React Native for App

## Hardware Used
- Raspberry Pi Zero W


# References
+ [HX711 Python module](https://github.com/gandalf15/HX711/)
+ [Raspi W Zero Hangboard](https://github.com/adrianlzt/piclimbing)
+ [Arduino Hangboard](https://github.com/oalam/isometryx)
