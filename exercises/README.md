# Exercises
This directory contains the exercise files and the corresponding classes for serving the timers.

## Preparation
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

# Running the backend
On OSX: 
```
python3 -m venv venv
source venv/bin/activate
./startup.sh
```

Using docker
```
docker build . -t exercise
docker run -p 4321:4321 --rm -it exercises
```

# Debugging the websockets
wscat -c "ws://127.0.0.1:4321/"


## Add new exercises
+ Create a new JSON file for the exercise.
