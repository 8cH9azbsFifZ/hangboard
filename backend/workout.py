"""
File containing all workout related classes.

This is the new thread based implementation of the classes.
Lessons learned: Microservices are fine, but nanoservices not :)
"""

import json
import os
import time

"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Workout(%(threadName)-10s) %(message)s',
                    )



import threading
"""
Use threading for threads
"""


from pydispatch import dispatcher
"""
Use pydispatch and signals to transfer JSON data between the threads.
"""

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

from messager import Messager
from sensor_zlagboard import SensorZlagboard
from board import Board
from board import AsciiBoard
from timers import PauseTimer
from timers import ExerciseTimer

class Workout():
    """
    All stuff for handling workouts containing sets of exercises.
    """
    def __init__(self, workoutfile="./../exercises/workouts/workout-test.json"):
        self.select_workout(workoutfile)
        self.exercise_status = "Status"
        self.workout_number = 0
        self.workout = (self.data["Workouts"][self.workout_number])
        self.workout_name = self.workout["Name"]
        self.total_sets = len (self.workout["Sets"])
        self.current_set = 0
        self.current_set_name = "Rest to start"

        # Variable to check if ready or somebody hanging
        self.exercise_hanging = False

        # Thread controlling
        self.do_stop = False

        # Signals handler setup
        dispatcher.connect( self.handle_signal_workout, signal=SIGNAL_WORKOUT, sender=dispatcher.Any )


    def select_workout(self, filename):
        self.workoutfile = filename # FIXME
        self.filename = self.workoutfile

        with open(self.filename) as json_file:
            self.data = json.load(json_file)

    def list_workouts(self):
        logging.debug("List workouts")
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

    def show_workout(self):
        print (self.data)

    def show_set(self):
        set = self.workout["Sets"][self.current_set]
        print (set)

    def show_exercise(self):
        exercise = self.workout["Sets"][self.current_set]["Exercise"]
        print (exercise)

    def run_workout (self):
        """
        Run a single workout
        """
        for w in range (0, self.total_sets+1):
            self.current_set = w
            self.run_set()

    def run_exercise_maximal_hang(self):
        logging.debug("Run a maximal hang time exercise")
        # TBD Implement

    def run_exercise_pull_ups(self):
        logging.debug("Run a pull ups exercise")
        # TBD Implement

    def __get_current_set(self):
        logging.debug('Get current set')

        self.exercise = self.workout["Sets"][self.current_set]["Exercise"]
        self.rest_to_start = self.workout["Sets"][self.current_set]["Rest-to-Start"]
        self.pause = self.workout["Sets"][self.current_set]["Pause"]
        self.reps = self.workout["Sets"][self.current_set]["Reps"]
        self.type = self.workout["Sets"][self.current_set]["Type"]
        self.left = self.workout["Sets"][self.current_set]["Left"]
        self.right = self.workout["Sets"][self.current_set]["Right"]
        self.counter = self.workout["Sets"][self.current_set]["Counter"]


    def run_pause(self):
        logging.debug('Run pause')

    def run_set(self):
        self.__get_current_set()
        logging.debug('Run exercise')
        self.rep_current = 0
        dispatcher.send( signal=SIGNAL_PAUSETIMER, message=self.rest_to_start)
        for self.rep_current in range (0, self.reps):
            self.__get_current_set()
            #print (self.rep_current)
            dispatcher.send( signal=SIGNAL_EXERCISETIMER, message=json.dumps(self.workout["Sets"][self.current_set]))
            #dispatcher.send( signal=SIGNAL_PAUSETIMER, message=self.pause)

    def handle_signal_workout (self, message):
        logging.debug('Signal detected with ' + str(message) )
        if (message == "RunSet"):
            self.run_set()
        if (message == "NoHangDetected"):
            dispatcher.send( signal=SIGNAL_EXERCISETIMER, message=json.dumps({"StopExerciseTimer": True}))
        if (message == "HangDetected"):
            dispatcher.send( signal=SIGNAL_EXERCISETIMER, message=json.dumps({"StartExerciseTimer": True}))

    def run_test (self):
        logging.debug('Run test')

        self.__get_current_set()
        dispatcher.send( signal=SIGNAL_EXERCISETIMER, message=json.dumps(self.workout["Sets"][self.current_set]))

                

