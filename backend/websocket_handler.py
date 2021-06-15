"""
This class provices all methods for websocket communication.
It is used in conjunction with the workout class in run_ws.py 
to start the backend serivce.
"""

import asyncio
import websockets

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Wensockets(%(threadName)-10s) %(message)s',
                    )

class WebsocketHandler():
    def __init__(self, sampling_interval = 0.1):
        logging.debug ("Init websocket handler")
        self.message = "" # Message for sending around :) 
        self.sampling_interval = sampling_interval

    def run_handler(self, wshost="0.0.0.0", wsport=4321):
        """
        Start the websocket server and wait for input
        """
        logging.debug ("Start handler")
        self.WSHOST = wshost
        self.WSPORT = wsport
        self.start_server = websockets.serve(self.handler, self.WSHOST, self.WSPORT)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    async def consumer_handler(self, websocket, path): # TODO: https://www.w3schools.com/python/python_inheritance.asp
        """
        Handler for receicing commands 
        """
        async for message in websocket:
            logging.debug ("Received it:")
            logging.debug (message)
            await self.consumer(message)

    async def consumer (self, message):
        """
        Execute commands as received from websocket (handler)
        """
        logging.debug("Received request: %s" % message)
        if (message == "Start"):
            self._run_workout() # FIXME: Document this is a sibling class which depends on the class methods in workout :) 
        if (message == "Stop"):
            self._stop_workout()     
        if (message == "GetBoardImage"):
            self._get_board_image_base64()
        if (message == "ListWorkouts"): 
           self._list_workouts()


    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
        while True:
            message = self.message 
            if (self.message == ""):
                await asyncio.sleep(self.sampling_interval) 
            else:
                await websocket.send(message)
                self.message = ""

    async def handler(self, websocket, path):
        """
        Handler for the websockets: Receiving and Sending
        """
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