"""! @brief Boards Backend with Doxygen comments."""

import time
import json
import argparse
import base64


from threading import Thread
import threading

import asyncio
import websockets

# Parse commandline
parser = argparse.ArgumentParser(description="Boards Backend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
args = parser.parse_args()

WSHOST = args.host 
WSPORT = args.port 

class Boards():
    def __init__(self, boardname = "zlagboard_evo"):
        self.boardname = boardname
        self.init_board()
    
    def run_handler(self):
        """
        Start the websocket server and wait for input
        """
        print ("Start handler")
        self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    def init_board (self):
        self.board_status = ""
        self.boardimage_base64 = ""
        self.boardfilename = "./" + self.boardname + "/holds.json" 

        with open(self.boardfilename) as json_file:
            self.boarddata = json.load(json_file)

        self.get_all_holds()

        self.boardname_full = self.boarddata["Name"]
        self.boardimagename = "./" + self.boardname + "/board.png" 

        self.get_image()

    def get_image(self):
        """
        Send board image as base64 over websocket
        """
        with open(self.boardimagename, "rb") as image_file:
            self.boardimage_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        self.board_status = self.boardimage_base64 

    def set_active_holds(self, array_holds):
        self.holds_active = array_holds
        self.holds_inactive = [x for x in self.all_holds if x not in array_holds]
        print (self.holds_active)
        print (self.holds_inactive)

    def get_all_holds(self):
        self.all_holds = []
        #print (self.boarddata["Holds"])
        for hold in self.boarddata["Holds"]:
            #print (hold["ImgLayerName"])
            self.all_holds.append(hold["ImgLayerName"])

    def get_hold_for_type(self, type):
        holds = []
        for hold in self.boarddata["Holds"]:
            if (hold["Name"] == type):
                holds.append(hold["ImgLayerName"])
        print (holds)

    async def consumer_handler(self, websocket, path): 
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
        if (message == "SetHolds"): # FIXME
            self.set_active_holds()  # FIXME: Parameter
        if (message == "GetBoard"):
            self.get_board()

    def get_board(self):
        """
        Get the board configuration (STUB)
        """
        # FIXME: Send response?
        #self.holds_active = [] # FIXME
        #self.holds_inactive = ["A1", "A7", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]
        
    def assemble_message(self):
        self.board_status = json.dumps({"HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, "BoardName": self.boardname, "BordImageName": self.boardimagename})

    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
        while True:
            message = self.board_status 
            await websocket.send(message)
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

if __name__ == "__main__":
    """
    Main Task
    """
    bb = Boards(boardname="zlagboard_evo")

    
    bb.run_handler()
