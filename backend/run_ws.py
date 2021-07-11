"""
Commandline interface to the hangboard - serving websockets
"""

from workout import Workout
   

"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    print ("Starting")
    wa = Workout(hostname="hangboard")
    #wa._set_workout(id="HRST-S-1-4ZBEVO")
    #wa._set_workout(id="ZB-A-1")
    wa._set_workout(id="WMVC-EASY-1")
    #wa._set_workout(id="WMVC-MODERATE-1")
    #wa._set_workout(id="WMVC-INTENSE-1")
    
    wa._core_loop()

