# Exercise Backend
import time
import json
import argparse

from threading import Thread
import threading

import asyncio
import websockets

parser = argparse.ArgumentParser(description="Workout Timer Backend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
args = parser.parse_args()

WSHOST = "127.0.0.1"# = args.host 
WSPORT = 4321 #= args.port 

workoutfile = "workout-test.json"

class Workout():
    def __init__(self):
        self.init_workout()
        self.init_board()
        #Thread.__init__(self)
        #self.active = True
        #self.daemon = True

        #self.start()

    def run_sender(self):
        print ("start sender")
        self.start_server = websockets.serve(self.exercisestatus, WSHOST, WSPORT)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()    
    
    def run_handler(self):
        print ("start handler")
        self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    def init_board (self):
        self.boardfilename = "../boards/zlagboard_evo/holds.json"

        with open(self.boardfilename) as json_file:
            self.boarddata = json.load(json_file)

        self.boardname = self.boarddata["Name"]
        self.boardimagename = "zlagboard_evo.svg"
        self.holds_active = ["A1", "A7"]
        self.holds_inactive = ["A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

        self.get_board()

    def init_workout(self):
        self.filename = workoutfile

        with open(self.filename) as json_file:
            self.data = json.load(json_file)

        self.exercise_status = "Status"
        self.workout_number = 0
        self.workout = (self.data["Workouts"][self.workout_number])
        self.workout_name = self.workout["Name"]
        self.total_sets = len (self.workout["Sets"])
        self.current_set = 0
        self.current_set_name = "Rest to start"

    async def exercisestatus(self, websocket, path):
        while True:
            sleept = 1
            await websocket.send(self.exercise_status)
            await asyncio.sleep(sleept)

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            print ("Received it:")
            print (message)
            await self.consumer(message)

    async def consumer (self, message):
            print("Received request: %s" % message)
            if (message == "Start"):
                self._run_set()
            if (message == "Stop"):
                self._stop_set()     
            if (message == "GetBoard"):
                self.get_board()

    def get_board(self):
        self.holds_active = []
        self.holds_inactive = ["A1", "A7", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]
        self.exercise_status = json.dumps({"Exercise": "Pause", "Duration": 0, "Counter": 0, "Completed": 0, "HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, "BoardName": self.boardname, "BordImageName": self.boardimagename, "TimerStatus": True})

    async def producer_handler(self, websocket, path):
        while True:
            message = self.exercise_status #await producer()
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

    def run_workout (self):
        for w in range (0, self.total_sets+1):
            self.current_set = w
            self.run_set()

    def _run_set (self):
        print ("Run thread set")
        self.run_set_thread = threading.Thread(target=self.run_set)
        self.run_set_thread.do_stop = False
        self.run_set_thread.start()

    def _stop_set (self):
        print ("Stop thread set")
        self.run_set_thread.do_stop = True

    def run_set (self):
        print ("Run one set")
        t = threading.currentThread()
        e = self.workout["Sets"][self.current_set]
        name = e["Exercise"]
        reps_total = e["Reps"]
        duration = e["Counter"]
        pause_duration = e["Pause"]
        rest_to_start = e["Rest-to-Start"]

        for reps_counter in range (1, 1+reps_total):
            if (getattr(t, "do_stop", False)):
                print ("Stop this stuff")
                return

            start_detected = 1
            if (start_detected == 1):
                if (name == "Hang"):
                    print ("Hang")
                    self.holds_active = ["A1", "A7"]
                    self.holds_inactive = ["A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]


                    for counter in range (0, duration+1):
                        time.sleep (1)
                        completed = int(counter / duration *100)
                        self.exercise_status = json.dumps({"Exercise": name, "Duration": duration, "Counter": counter, "Completed": completed, "HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, "BoardName": self.boardname, "BordImageName": self.boardimagename, "TimerStatus": self.run_set_thread.do_stop})
                        if (getattr(t, "do_stop", False)):
                            print ("Stop this stuff")
                            return
                elif (name == "Maximal Hang"):
                    print ("Key press?")                    
                elif (name == "Assisted Pull Ups"):
                    print ("Key press?")                    
                else:
                    print ("Key press?")

                if (getattr(t, "do_stop", False)):
                    print ("Stop this stuff")
                    return

                print ("Pause")
                self.holds_active = []
                self.holds_inactive = ["A1", "A7", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

                for counter in range (0, pause_duration+1):
                    time.sleep (1)
                    completed = int(counter / pause_duration *100)
                    self.exercise_status = json.dumps({"Exercise": "Pause", "Duration": pause_duration, "Counter": counter, "Completed": completed, "HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, "BoardName": self.boardname, "BordImageName": self.boardimagename, "TimerStatus": self.run_set_thread.do_stop})
                    if (getattr(t, "do_stop", False)):
                        print ("Stop this stuff")
                        return


if __name__ == "__main__":
    ex = Workout()
    #ex.run_sender()
    ex.run_handler()
    while True:
        print ("Exercise Timer Backend running")
        time.sleep(1)
