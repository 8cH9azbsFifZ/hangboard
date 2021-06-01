"""
Exercise Backend
"""

# Exercise Backend
import time
import json
import argparse
import os

from threading import Thread
import threading

import asyncio
import websockets

# Parse commandline
parser = argparse.ArgumentParser(description="Workout Timer Backend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
args = parser.parse_args()

WSHOST = args.host 
WSPORT = args.port 

workoutfile = "./workouts/workout-test.json" # FIXME

class Workout():
    def __init__(self):
        self.init_workout()
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
        #self.boardfilename = "../boards/zlagboard_evo/holds.json"
        self.boardfilename = "./boards/holds.json" # FIXME

        with open(self.boardfilename) as json_file:
            self.boarddata = json.load(json_file)

        self.boardname = self.boarddata["Name"]
        self.boardimagename = "zlagboard_evo.svg" ## FIXME
        self.holds_active = ["A1", "A7"] # FIXME
        self.holds_inactive = ["A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

        self.get_board() # FIXME: link to new board class

    def list_workouts(self):
        self.workoutdir = "./workouts"
        for filename in os.listdir (self.workoutdir):
            if filename.endswith ("json"):
                fn = os.path.join(self.workoutdir, filename)
                with open(fn) as json_file:
                    data = json.load(json_file)
                    #print (data)
                    #workout = (data["Workouts"])
                    #print (workout)
                    for workout in (data["Workouts"]):
                    #    print ("ok")
                        print (workout["Name"], fn)


    def init_workout(self):
        """
        Initialize a new workout run
        """
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

    def get_board(self):
        """
        Get the board configuration (STUB)
        """
        self.holds_active = [] # FIXME
        self.holds_inactive = ["A1", "A7", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]
        self.exercise_status = json.dumps({"Exercise": "Pause", "Duration": 0, "Counter": 0, "Completed": 0, "HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, "BoardName": self.boardname, "BordImageName": self.boardimagename, "TimerStatus": True})

    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
        while True:
            message = self.exercise_status 
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

    def run_workout (self):
        """
        Run a single workout
        """
        for w in range (0, self.total_sets+1):
            self.current_set = w
            self.run_set()

    def _run_set (self):
        """
        Start a workout "set" in a thread
        """
        print ("Run thread set")
        self.run_set_thread = threading.Thread(target=self.run_set)
        self.run_set_thread.do_stop = False
        self.run_set_thread.start()

    def _stop_set (self):
        """
        Stop a workout "set" thread" by setting a flag, which must be caputured in "run_set".
        """
        print ("Stop thread set")
        self.run_set_thread.do_stop = True

    def run_set (self):
        """
        Run Set Function with main logic
        """
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
    """
    Main Task
    """
    ex = Workout()
    #ex.run_handler()
    ex.list_workouts()

