"""
Commandline interface to the hangboard - serving websockets
"""

from workout import Workout
from websocket_handler import WebsocketHandler


class Hangboard(Workout, WebsocketHandler):
    def __init__(self, verbose=None):
        super(Hangboard, self).__init__()
    

    

"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    print ("Starting")
    wa = Hangboard()
    wa.run_handler()
    #wa.show_workout()
    #wa._run_workout()
    #wa.run_websocket_handler()