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
    def __init__(self, verbose=None, dt=0.1, workoutfile="./../exercises/workouts/workout-test.json"):
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
        logging.debug("Running workout")
        for self.current_set in range (0, self.total_sets):
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
        for self.rep_current in range (0, self.reps):
            print (self.rep_current)

