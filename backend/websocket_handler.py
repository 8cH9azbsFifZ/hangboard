import asyncio
import websockets


class WebsocketHandler():

    def __init__():
        pass

    def run_handler(self):
        """
        Start the websocket server and wait for input
        """
        print ("Start handler")
        self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    async def consumer_handler(self, websocket, path): # TODO: https://www.w3schools.com/python/python_inheritance.asp
        """
        Handler for receicing commands 
        """
        async for message in websocket:
            print ("Received it:")
            print (message)
            await self.consumer(message)

    async def consumer (self, message):
        """
        Execute commands as received from websocket (handler)
        """
        print("Received request: %s" % message)
        if (message == "Start"):
            self._run_set()
        if (message == "Stop"):
            self._stop_set()     
        if (message == "GetBoard"):
            self.get_board()
        if (message == "ListWorkouts"): # TBD: Implement in webinterface
            self.list_workouts()


    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
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