"""
Commandline interface to the hangboard - serving websockets
"""

from workout import Workout
from websocket_handler import WebsocketHandler
from mqtt_handler import MQTT_Handler

USE_WEBSOCKETS = False
USE_MQTT = not USE_WEBSOCKETS

if USE_WEBSOCKETS:
    class Hangboard(Workout, WebsocketHandler):
        def __init__(self, verbose=None):
            super(Hangboard, self).__init__()
if USE_MQTT:
    class Hangboard(Workout, MQTT_Handler):
        def __init__(self, verbose=None):
            super(Hangboard, self).__init__()
    

"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    print ("Starting")
    wa = Hangboard()
    if USE_WEBSOCKETS:
        wa.run_handler(hostname="localhost", port=4321)
    if USE_MQTT:
        wa.run_handler(hostname="localhost", port=1883)
        # FIXME

    #wa.show_workout()
    #wa._run_workout()
    #wa.run_websocket_handler()