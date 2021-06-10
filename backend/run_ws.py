"""
Commandline interface to the hangboard - serving websockets
"""


from messager import Messager
from sensor_zlagboard import SensorZlagboard
from board import Board
from board import AsciiBoard
from timers import PauseTimer
from timers import ExerciseTimer
from workout import Workout

"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    print ("Starting")