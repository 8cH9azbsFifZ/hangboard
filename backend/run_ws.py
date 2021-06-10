"""
Commandline interface to the hangboard - serving websockets
"""

from workout import Workout
from messager import Messager

class BackendWorkout(Workout, Messager):
    def __init__(self, verbose=None):
        super(BackendWorkout, self).__init__()


"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    print ("Starting")
    wa = Workout()
    #wa.show_workout()
    wa.run_workout()
    #wa.run_websocket_handler()