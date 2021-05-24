# Hangboard 

*STATUS: In Development*

Force and velocity sensing hangboard mount with exercise timers for all hangboards.
![Hangboard Mount](./images/IsometrixBoard.png|width=100)

# Developing

## Preparation
``` 
sudo apt-get install -y python3-pip
cd hangboard-app
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running the Demonstrator
+ Start the Web App: `python3 main.py`
+ Start Exercises `python3 exercise.py`
+ Start CLI Dumper `python3 cli.py`

## Software Used
- Python Flask for Web App
- Zero MQ for Communication
- JSON for Board configuration
- SVG Layers for hold configuration


# References
+ [HX711 Python module](https://github.com/gandalf15/HX711/)
+ [Raspi W Zero Hangboard](https://github.com/adrianlzt/piclimbing)
+ [Arduino Hangboard](https://github.com/oalam/isometryx)

