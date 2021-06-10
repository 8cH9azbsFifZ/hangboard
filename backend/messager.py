"""
Class for handling all communications from the backend to the frontend.
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Messager(%(threadName)-10s) %(message)s',
                    )


import time
import asyncio
import threading
import websockets
import os

WSHOST = "0.0.0.0" #args.host 
WSPORT = 4321 #args.port 


#class Messager(threading.Thread):
class Messager():
    """
    All stuff for sending the data created in this file using websockets to the frontends.
    """
    def __init__(self):
        self.daemon = True
        logging.debug ("Init class for messager")
        self.do_stop = False

        self.sampling_interval = 0.1

        self.ws_msg = "Alive"



    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        logging.debug ("Starting thread for messager")

        self.run_websocket_handler()

    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
        while True:
            await websocket.send(self.ws_msg)
            #if "OneMessageOnly" in self.exercise_status:
            #    self.exercise_status = ""
            await asyncio.sleep(self.sampling_interval) 

    async def handler(self, websocket, path):
        """
        Handler for the websockets: Receiving and Sending
        """
        # TODO rework for this version
        consumer_task = asyncio.ensure_future(            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(            self.producer_handler(websocket, path))
        #pipe_task = asyncio.ensure_future(            self.pipe_handler())
        queue_task = asyncio.ensure_future(            self.queue_handler())

        #done, pending = await asyncio.wait(            [consumer_task, producer_task, pipe_task],            return_when=asyncio.FIRST_COMPLETED,
        done, pending = await asyncio.wait(            [consumer_task, producer_task, queue_task],            return_when=asyncio.FIRST_COMPLETED,
        #done, pending = await asyncio.wait(            [consumer_task, producer_task],            return_when=asyncio.FIRST_COMPLETED,
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
            SIGNAL_AIO_WORKOUT.send("RunSet") #print ("AHA")
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

        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()
    