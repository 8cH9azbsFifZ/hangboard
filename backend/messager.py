"""
Class for handling all communications from the backend to the frontend.
"""


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Messager(%(threadName)-10s) %(message)s',
                    )


from pydispatch import dispatcher

import time
import asyncio
import websockets

WSHOST = "0.0.0.0" #args.host 
WSPORT = 4321 #args.port 

import janus


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


class Messager():
    """
    All stuff for sending the data created in this file using websockets to the frontends.
    """
    def __init__(self):
        logging.debug ("Init class for messager")
        self.do_stop = False

        self.sampling_interval = 0.1

        self.ws_msg = "Alive"

        dispatcher.connect( self.handle_signal, signal=SIGNAL_MESSAGER, sender=dispatcher.Any )

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        logging.debug ("Starting thread for messager")

        self.run_websocket_handler()

    def handle_signal (self, message):
        logging.debug('Messager: Signal detected with ' + str(message) )
        self.ws_msg = str(message)

    def run_websocket_handler(self):
        """
        Start the websocket server and wait for input
        """
        logging.debug ("Start websocket handler")
        #queue = janus.Queue()

        #self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)

        #asyncio.get_event_loop().run_until_complete(self.start_server)
        #asyncio.get_event_loop().run_forever()




#            dispatcher.send( signal=SIGNAL_WORKOUT, message="RunSet")