"""
Class for handling all communications from the backend to the frontend.
"""


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Messager(%(threadName)-10s) %(message)s',
                    )


import threading
from pydispatch import dispatcher

import time
import asyncio
import websockets

WSHOST = "0.0.0.0" #args.host 
WSPORT = 4321 #args.port 


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


    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
        # TODO rework for this version
        while True:
            message = self.exercise_status 
            await websocket.send(message)
            if "OneMessageOnly" in self.exercise_status:
                self.exercise_status = ""
            await asyncio.sleep(1) 

    async def handler(self, websocket, path):
        """
        Handler for the websockets: Receiving and Sending
        """
        # TODO rework for this version
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket, path))

        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    async def consumer_handler(self, websocket, path): 
        """
        Handler for receicing commands 
        """
        # TODO rework for this version

        async for message in websocket:
            print ("Received it:")
            print (message)
            await self.consumer(message)

    async def consumer (self, message):
        """
        Execute commands as received from websocket (handler)
        """
        # TODO rework for this version

        print("Received request: %s" % message)
        if (message == "Start"):
            self._run_set()
        if (message == "Stop"):
            self._stop_set()     
        if (message == "GetBoard"):
            self.get_board()
        if (message == "ListWorkouts"): # TBD: Implement in webinterface
            self.list_workouts()
        if (message == "StartHang"):
            self.set_start_hang()
        if (message == "StopHang"):
            self.set_stop_hang()

    def run_websocket_handler(self):
        """
        Start the websocket server and wait for input
        """
        # TODO rework for this version

        print ("Start handler")
        self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()