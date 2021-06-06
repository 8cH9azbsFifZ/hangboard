"""
Exercise Backend:
Containes all features for running a hangboard timer.
It provides timer for exercises and sets, which can be controlled via websockets.
"""

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
        self.boardimagename = "zlagboard_evo.svg" ## FIXME: use board service
        self.holds_active = ["A1", "A7"] # FIXME
        self.holds_inactive = ["A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

        self.get_board() # FIXME: link to new board class

    def list_workouts(self):
        print ("List workouts")
        self.workoutdir = "./workouts"
        workout_array = []
        
        for filename in os.listdir (self.workoutdir):
            if filename.endswith ("json"):
                fn = os.path.join(self.workoutdir, filename)
                with open(fn) as json_file:
                    data = json.load(json_file)

                    for workout in (data["Workouts"]):
                        print (workout["Name"], fn)
                        workout_array.append({"Name": workout["Name"], "ID": workout["ID"]})
        print (workout_array)
        
        self.exercise_status = json.dumps({"WorkoutList": workout_array, "OneMessageOnly": True})

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
        self.current_set_reps_total = 0
        self.current_set_reps_current = 0

        # Time increment for counter
        self.exercise_dt = 0.1

        # Variables for the status of one exercise in a set / run
        self.exercise_duration = 0
        self.exercise_name = ""
        self.exercise_completed = 0
        self.exercise_counter = 0

        # Variable to check if ready or somebody hanging
        self.exercise_hanging = False

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

    def set_start_hang(self):
        """
        Set flag wether a hang is detected or not.
        """ 
        print ("Start to hang")
        self.exercise_hanging = True

    def set_stop_hang(self):
        """
        Set flag wether a hang is detected or not.
        """ 
        print ("Stopped to hang")
        self.exercise_hanging = False

    def get_board(self):
        """
        Get the board configuration (STUB)
        """
        self.holds_active = [] # FIXME: get from board service
        self.holds_inactive = ["A1", "A7", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]
        #self.exercise_status = json.dumps({"Exercise": "Pause", "Duration": 0, "Counter": 0, "Completed": 0, "HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, "BoardName": self.boardname, "BordImageName": self.boardimagename, "TimerStatus": True})
        self.assemble_message()

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

        self.current_set_reps_total = reps_total

        for reps_counter in range (1, 1+reps_total):
            self.current_set_reps_current = reps_counter
            if (getattr(t, "do_stop", False)):
                print ("Stop this stuff")
                return

            while not self.exercise_hanging:
                #print ("No hang yet")
                time.sleep(0.1)

            if (name == "Hang"):
                self.run_exercise_hang()
            elif (name == "Maximal Hang"):
                self.run_exercise_maximal_hang()
            elif (name == "Assisted Pull Ups"):
                self.run_exercise_pull_ups()
            else:
                print ("Key press?")

            if (getattr(t, "do_stop", False)):
                print ("Stop this stuff")
                return

            while self.exercise_hanging:
                #print ("Still hanging around")
                time.sleep(0.1)

            self.run_exercise_pause()

    def run_exercise_hang(self):
        t = threading.currentThread()
        e = self.workout["Sets"][self.current_set]
        self.exercise_duration = e["Counter"]
        self.exercise_name = e["Exercise"]

        print ("Run a hang exercise")
        self.holds_active = ["A1", "A7"] # FIXME
        self.holds_inactive = ["A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]


        for self.exercise_counter in range (0, self.exercise_duration+1):
            time.sleep (1) # FIXME: smaller timer interval
            self.exercise_completed = int(self.exercise_counter / self.exercise_duration*100)
            self.assemble_message()

            if (self.exercise_hanging == False): # of nobody hanging - quit
                return

            if (getattr(t, "do_stop", False)):
                print ("Stop this stuff")
                return

    def run_exercise_maximal_hang(self):
        print ("Run a maximal hang time exercise")
        # TBD Implement

    def run_exercise_pull_ups(self):
        print ("Run a pull ups exercise")
        # TBD Implement

    def run_exercise_pause(self):
        print ("Run a pause between exercises")
        e = self.workout["Sets"][self.current_set]
        t = threading.currentThread()
        self.exercise_duration = e["Pause"]
        self.exercise_name = "Pause"

        self.holds_active = [] # FIXME
        self.holds_inactive = ["A1", "A7", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

        for self.exercise_counter in range (0, self.exercise_duration+1):
            time.sleep (1)
            self.exercise_completed = int(self.exercise_counter / self.exercise_duration*100)
            self.assemble_message()

            if (self.exercise_hanging == True): # of somebody hanging - quit
                return

            if (getattr(t, "do_stop", False)):
                print ("Stop this stuff")
                return

    def assemble_message(self):
        """
        Assemble a message of the current exercise and workout status
        """
        if (hasattr(self, "run_set_thread")):
            self.exercise_status = json.dumps({"Exercise": self.exercise_name, "Duration": self.exercise_duration, "Counter": self.exercise_counter, "Completed": self.exercise_completed, 
            "HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, 
            "BoardName": self.boardname, "BordImageName": self.boardimagename, 
            "TimerStatus": self.run_set_thread.do_stop,
            "WorkoutName": self.workout_name, "CurrentExercise": self.exercise_name, "CurrentExerciseCounter": self.exercise_duration, "CurrentSet": self.current_set, "TotalSets": self.total_sets,
            "CurrentSetRep": self.current_set_reps_current, "CurrentSetRepTotal": self.current_set_reps_total
            })
        else:
            self.exercise_status = json.dumps({"Exercise": self.exercise_name, "Duration": self.exercise_duration, "Counter": self.exercise_counter, "Completed": self.exercise_completed, 
            "HoldsActive": self.holds_active, "HoldsInactive": self.holds_inactive, 
            "BoardName": self.boardname, "BordImageName": self.boardimagename, 
            "WorkoutName": self.workout_name, "CurrentExercise": self.exercise_name, "CurrentExerciseCounter": self.exercise_duration, "CurrentSet": self.current_set, "TotalSets": self.total_sets,
            "CurrentSetRep": self.current_set_reps_current, "CurrentSetRepTotal": self.current_set_reps_total
            })

if __name__ == "__main__":
    """
    Main Task
    """
    ex = Workout()
    ex.run_handler()
