"""
Commandline interface to the hangboard - serving websockets
"""

from workout import Workout

"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    print ("Starting")
    wa = Workout()
    #wa.show_workout()
    wa.run_workout()