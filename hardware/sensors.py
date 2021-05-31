import time
import json
import argparse

from threading import Thread
import threading

import asyncio
import websockets

#from hx711 import HX711


parser = argparse.ArgumentParser(description="Sensors Backend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
args = parser.parse_args()

WSHOST = "127.0.0.1"# = args.host 
WSPORT = 9091 #= args.port 


class Sensors():
    def __init__(self):
        print ("Init sensors")
        self.sensor_status = "None"

    def run_handler(self):
        print ("start handler")
        self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            print ("Received it:")
            print (message)
            await self.consumer(message)

    async def consumer (self, message):
            print("Received request: %s" % message)
            if (message == "Start"):
                self._run_simulation()

    async def producer_handler(self, websocket, path):
        while True:
            message = self.sensor_status #await producer()
            await websocket.send(message)
            await asyncio.sleep(1) #new

    async def handler(self, websocket, path):
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

    def _run_simulation (self):
        print ("Run thread simulation")
        self.run_thread = threading.Thread(target=self.run_simulation)
        self.run_thread.do_stop = False
        self.run_thread.start()

    def _stop_simulation (self):
        print ("Stop thread simulation")
        self.run_thread.do_stop = True

    def run_simulation(self):
        self.sensor_status = json.dumps({"SensorStatus": self.run_thread.do_stop})

if __name__ == "__main__":
    sns = Sensors()
    sns.run_handler()


