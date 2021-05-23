# Hangboard 


## Preparation
# sudo apt-get install -y python3-pip


## Developing
```
cd hangboard-app
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

## Adding a new board
Getting X and Y coordinates of an image in browser:
https://stackoverflow.com/questions/12888584/is-there-a-way-to-tell-chrome-web-debugger-to-show-the-current-mouse-position-in

Use inkscape with layers

# References
+ https://github.com/gandalf15/HX711/
+ https://realpython.com/python-web-applications/
+ https://github.com/djdmorrison/flask-progress-example
+ https://github.com/adrianlzt/piclimbing
+ https://github.com/helloflask/timer
+ https://github.com/tecladocode/hiit-timer

# History
- v0.5 - Jug selection and timer integrated demonstrator
- v0.4 - SVG layers demonstrator integrated and cleanup
- v0.3 - SVG layers proof of concept working
- v0.2 - ZMQ demonstrator working
- v0.1 - Timer and progress bar demonstrator working