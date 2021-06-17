"""
This class provices all methods for websocket communication.
It is used in conjunction with the workout class in run_ws.py 
to start the backend serivce.

This class receives all commands from the frontend and controls the backend processes.
"""

import asyncio
import websockets

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Websockets(%(threadName)-10s) %(message)s',
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
        logging.debug ("Start websocket handler")
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
            logging.debug ("Received the command: " + str(message))
            await self.consumer(message)

    async def consumer (self, message):
        """
        Execute commands as received from websocket (handler)
        """
        logging.debug("Received request: %s" % message)
        if (message == "Start"):
            """
Example output during run:
< {"Exercise": "Hang", "Type": "Hang", "Left": "A1", "Right": "A7", "Counter": "10.00", "CurrentCounter": "1.00", "Completed": "10", "Rest": "9.00", "HangChangeDetected": "", "HangDetected": true, "FTI": 88.446509551602, "AverageLoad": 7.6098875305079865, "MaximalLoad": 8.27237052022345, "RFD": 12.0508714305325, "LoadLoss": 0.08722646276079593}

            """
            self._run_workout() # FIXME: Document this is a sibling class which depends on the class methods in workout :) 
        if (message == "Stop"):
            self._stop_workout()     
        if (message == "GetBoardImage"):
            self._get_board_image_base64()
        if (message == "ListWorkouts"): 
            self._list_workouts()
        if (message == "GetCurrentWorkout"):
            self._get_current_workout()
        if (message == "GetCurrentMeasurementsSeries"):
            """
Example output: 
GetCurrentMeasurementsSeries
< {"CurrentMeasurementsSeries": {"time": [1623841943.9033473, 1623841944.0089374, 1623841944.1252787, 1623841944.242679, 1623841944.3611054, 1623841944.4760737, 1623841944.593933, 1623841944.7120495, 1623841944.8308997, 1623841944.945941], "load": [5.207050304689482, 6.479503085064949, 7.367424467332381, 8.233546732602022, 8.235494204149376, 8.123420357682338, 8.185299695557916, 8.25547149292545, 8.27237052022345, 7.798381074262804]}}

            """
            self._get_current_measurements_series()


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