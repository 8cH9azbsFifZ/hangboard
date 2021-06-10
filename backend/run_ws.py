"""
Commandline interface to the hangboard - serving websockets
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
from aio_pydispatch import Signal

SIGNAL_AIO_MESSAGER = Signal('SignalMessager')
SIGNAL_AIO_WORKOUT = Signal('SignalWorkout')

#from pydispatch import dispatcher
import pydispatch
from queMorph import *

from multiprocessing import Process, Queue

"""
The main loop is used for testing currently.
"""
if __name__ == "__main__":
    mm = Messager()

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
    #dispatcher.send( signal=SIGNAL_ZLAGBOARD, message="Calibrate")
    #zlb.calibrate()

    #p = Process(target=my_function, args=(queue, 1))
    #p.start()
    #p.join() # this blocks until the process terminates

    wa = Workout()
    #wa.start()
    #pydispatch.dispatcher.send( signal=SIGNAL_WORKOUT, message="RunSet")
    #wa.run_set()
    mm.run()
    #mm.start()
