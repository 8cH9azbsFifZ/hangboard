# Hangboard Hold configuration
This directory contains the hold configurations for different boards

# Boards
## Zlagboard EVO

## Zlagboard Mini

## Beastmaker 1000
+ Hold sizes: https://rupertgatterbauer.com/beastmaker-1000/#:~:text=Speaking%20of%20design%2C%20the%20Beasmaker,slopers%20and%20pull%2Dup%20jugs.

## Beastmaker 2000

# Run the module
On OSX: 
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```
Using docker
```
docker build . -t boards
docker run -p 4324:4324 --rm -it boards
```


## Debugging the websockets
wscat -c "ws://10.101.40.81:4324/"


## Test the module
```
python3 test_boards.py      
```

# Implement new board configurations

## Preparation
+ Install inkscape `brew install inkscape`

## Work
+ Create a new board json file 
+ Use inkscape with layers for overlay image creation 
+ Edit layer "id" names manually afterwards
+ change all style:: display:inline => inline
+ Export all layers as svg and convert them to png (i.e. https://svgtopng.com/de/)
