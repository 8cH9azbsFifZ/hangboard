"""
Class for handling all communications from the backend to the frontend.
"""


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Messager(%(threadName)-10s) %(message)s',
                    )


from pydispatch import dispatcher
from aio_pydispatch import Signal

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

SIGNAL_AIO_MESSAGER = Signal('SignalMessager')

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

class Messager():
    """
    All stuff for sending the data created in this file using websockets to the frontends.
    """
    def __init__(self):
        logging.debug ("Init class for messager")
        self.do_stop = False

        self.sampling_interval = 0.1

        #dispatcher.connect( self.handle_signal, signal=SIGNAL_MESSAGER, sender=dispatcher.Any )
        SIGNAL_AIO_MESSAGER.connect(self.handle_signal)

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        logging.debug ("Starting thread for messager")

        self.run_websocket_handler()
        #while True:
        #    if (self.do_stop == True):
        #        return
        #    time.sleep(self.sampling_interval)
        #return

    def handle_signal (self, message):
        logging.debug('Messager: Signal detected with ' + str(message) )
        self.start_server.send(message)

    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
        # TODO rework for this version
        while True:
            message = "Alive" #self.exercise_status 
            await websocket.send(message)
            #if "OneMessageOnly" in self.exercise_status:
            #    self.exercise_status = ""
            await asyncio.sleep(self.sampling_interval) 

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
        if (message == "RunSet"):
            print ("AHA")
            #dispatcher.send( signal=SIGNAL_WORKOUT, message="RunSet")
        #if (message == "Start"):
        #    self._run_set()
        #if (message == "Stop"):
        #    self._stop_set()     
        #if (message == "GetBoard"):
        #    self.get_board()
        #if (message == "ListWorkouts"): # TBD: Implement in webinterface
        #    self.list_workouts()
        #if (message == "StartHang"):
        #    self.set_start_hang()
        #if (message == "StopHang"):
        #    self.set_stop_hang()

    def run_websocket_handler(self):
        """
        Start the websocket server and wait for input
        """
        logging.debug ("Start websocket handler")
        self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)
        
        #get_or_create_eventloop
        #loop = get_or_create_eventloop()
        #loop.run_until_complete(self.start_server)
        #loop.run_forever()
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()