

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Messager(%(threadName)-10s) %(message)s',
                    )


import threading
from pydispatch import dispatcher

import time


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


class Messager(threading.Thread):
    """
    All stuff for sending the data created in this file using websockets to the frontends.
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(Messager,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_MESSAGER, sender=dispatcher.Any )

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while True:
            if (self.do_stop == True):
                return
            time.sleep(1)
        return

    def handle_signal (self, message):
        logging.debug('Messager: Signal detected with ' + str(message) )

