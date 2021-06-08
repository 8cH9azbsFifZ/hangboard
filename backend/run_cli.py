"""
Commandline interface to the hangboard
"""


"""
Signals for communication
"""
SIGNAL_WORKOUT = 'SignalWorkout'
SIGNAL_MESSAGER = 'SignalMessager'
SIGNAL_EXERCISETIMER = 'SignalExerciseTimer'
SIGNAL_PAUSETIMER = 'SignalPauseTimer'
SIGNAL_ASCIIBOARD = 'AsciiBoard'
SIGNAL_BOARD = 'Board'
SIGNAL_ZLAGBOARD = "SignalZlagboard"

from messager import Messager
from sensor_zlagboard import SensorZlagboard
from board import Board
from board import AsciiBoard
from timers import PauseTimer
from timers import ExerciseTimer
from workout import Workout

#from pydispatch import dispatcher
import pydispatch


"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    mm = Messager()
    mm.start()
    ex = ExerciseTimer(dt=1)
    ex.start()
    pa = PauseTimer(dt=1)
    pa.start()
    bb = Board()
    bb.start()
    ab = AsciiBoard()
    ab.start()
    zlb = SensorZlagboard()
    zlb.start()
    wa = Workout()
    pydispatch.dispatcher.send( signal=SIGNAL_WORKOUT, message="RunSet")

