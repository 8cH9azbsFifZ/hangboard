#!/bin/bash

# Only for OSX
#python3 -m venv venv
#source venv/bin/activate

# Startup exercises task
cd exercises
#python3 -m pip install -r requirements.txt
python3 exercises.py --host 0.0.0.0 --port 4321 &
cd ..

# Gyroscope
cd hardware/gyroscope
#python3 -m pip install -r requirements.txt
python3 sensor_zlagboard.py --host 0.0.0.0 --port 4323 &
cd ../..


# Board
cd boards
#python3 -m pip install -r requirements.txt
python3 boards.py --host 0.0.0.0 --port 4324 &
cd ..

# Webinterface
cd hangboard-web
#python3 -m pip install -r requirements.txt
python3 main.py --host 0.0.0.0 --port 8080 
cd ..