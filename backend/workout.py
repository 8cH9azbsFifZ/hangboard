"""
File containing all workout related classes.

This is the new thread based implementation of the classes.
Lessons learned: Microservices are fine, but nanoservices not :)
"""

import json
import os
import time
import sys
import threading


"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Workout(%(threadName)-10s) %(message)s',
                    )

from board import Board
from sensors import Sensors


class Workout():
    """
    All stuff for handling workouts containing sets of exercises.
    """
    def __init__(self, verbose=None, dt=0.1, workoutdir="../exercises/workouts", workoutfile="workout-test.json"):
        self.workoutdir = workoutdir
        self.select_workout(workoutdir + "/" + workoutfile)
        self.exercise_status = "Status"
        self.workout_number = 0
        self.workout = (self._data["Workouts"][self.workout_number])
        self.workout_name = self.workout["Name"]
        self.total_sets = len (self.workout["Sets"])
        self.current_set = 0
        self.current_set_name = "Rest to start"
        self.sampling_interval = dt

        # Variable to check if ready or somebody hanging
        self.exercise_hanging = False

        self.exercise_dt = dt

        # Variable storing the message for the "middleware" -> Sending
        self.message = ""

        # State of the current workout
        self._workout_running = False

        self.board = Board()
        self.sensors = Sensors()


    def select_workout(self, filename):
        """ Select a workout based on a filename. """
        self.workoutfile = filename # FIXME
        self.filename = self.workoutfile

        with open(self.filename) as json_file:
            self._data = json.load(json_file)

    def _get_current_workout(self):
        """
        Print the total current workout and it in the messaging queue (self.message)
        """
        logging.debug("Get current workout")
        self.message = json.dumps({"CurrentWorkout": self._data})

    def _calc_time_in_current_workout(self):
        """
        Caluculate total time, estimated rest time and planned time in this workout so far
        """
        total_time = 0
        estimated_rest_time = 0
        planned_time_sofar = 0

        for s in range (0, self.total_sets-1):
            resttostart = self.workout["Sets"][s]["Rest-to-Start"]
            pause = self.workout["Sets"][s]["Pause"]
            reps = self.workout["Sets"][s]["Reps"]
            counter = self.workout["Sets"][s]["Counter"]
            settime = resttostart + reps * (counter + pause)
            if (self.current_set <= s):
                planned_time_sofar = planned_time_sofar + settime
            total_time = total_time + settime

        estimated_rest_time = total_time - planned_time_sofar
        return [total_time, planned_time_sofar, estimated_rest_time]


    def _list_workouts(self):
        """
        Get list of available workouts and put it in the messaging queue (self.message)
        """
        logging.debug("List workouts")
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
        self.message = json.dumps({"WorkoutList": workout_array})

    def show_set(self): 
        """ Ascii output of current set """
        set = self.workout["Sets"][self.current_set]
        print (set)

    def show_exercise(self):
        """ Ascii output of current exercise """
        exercise = self.workout["Sets"][self.current_set]["Exercise"]
        print (exercise)

    def run_exercise_1hand_pull(self): # TODO implement
        """
        Run an exercise for 1 hand pulls. Given a maximum load a climber can handle and the given intensity
        the threshold load to be applied is:
        Threshold >= Load_max * Intensity
        """
        intensity = 0.5
        load_max = 44
        threshold = intensity * load_max

        pass


    def run_workout (self):
        """
        Run a single workout
        """
        logging.debug("Running workout")
        for self.current_set in range (0, self.total_sets):
            self.run_set()

    def run_exercise_maximal_hang(self):
        """ Run a maximal hang exercises """
        logging.debug("Run a maximal hang time exercise")
        # TBD Implement

    def run_exercise_pull_ups(self):
        """ Run pull up exercise """
        logging.debug("Run a pull ups exercise")
        # TBD Implement
        # TODO counting - how to achieve (force or distance detection?)

    def __get_current_set(self):
        """ Get parameters of the current set """
        logging.debug('Get current set')

        self.exercise = self.workout["Sets"][self.current_set]["Exercise"]
        self.rest_to_start = self.workout["Sets"][self.current_set]["Rest-to-Start"]
        self.pause = self.workout["Sets"][self.current_set]["Pause"]
        self.reps = self.workout["Sets"][self.current_set]["Reps"]
        self.type = self.workout["Sets"][self.current_set]["Type"]

        holdtypeleft = self.workout["Sets"][self.current_set]["Left"]
        holdtyperight = self.workout["Sets"][self.current_set]["Right"]
        
        self.left = self.board.get_hold_for_type(holdtypeleft)[0]
        self.right = self.board.get_hold_for_type(holdtyperight)[-1]

        self.counter = self.workout["Sets"][self.current_set]["Counter"]

    def _get_board_image_base64(self):
        """ Get the base64 image of the current board and put it in the message queue as base64 """
        image_base64 = self.board.svg._get_image_base64()
        print (image_base64)
        self.message = image_base64

    def _assert_nobody_hanging(self):
        """ Wait until nobody is hanging on the board """
        #logging.debug ("Keiner dran?")
        self.sensors.run_one_measure()
        while self.sensors.HangDetected == True:
            time.sleep(self.sampling_interval)
            self.sensors.run_one_measure()

    def _assert_somebody_hanging(self):
        """ Wait until somebody is hanging on the board. """
        #logging.debug("Jemand dran?")
        self.sensors.run_one_measure()
        while self.sensors.HangDetected == False:
            time.sleep(self.sampling_interval)
            self.sensors.run_one_measure()

    def run_rest_to_start(self):
        """ Run a pause in advance of a new set. """
        logging.debug("Rest to start loop")
        t = threading.currentThread()
        self.exercise_t = 0
        self.sensors.run_one_measure()
        self._assert_nobody_hanging() #FIXME
        while (float(self.exercise_t) < float(self.rest_to_start - self.epsilon)):
            time.sleep (self.exercise_dt)
            self.exercise_t = self.exercise_t + self.exercise_dt
            self.exercise_rest = self.rest_to_start - self.exercise_t
            self.exercise_completed = float(self.exercise_t) / float(self.rest_to_start) *100
            self.sensors.run_one_measure()
            #print ("%d of %d (%f percent) rest to start." % (self.exercise_t, self.rest_to_start, self.exercise_completed)) 
            self.assemble_message_resttostart_timerstatus()
            if (self.sensors.Changed == "Hang"):
                break
            if (getattr(t, "do_stop", False)):                
                break

    def run_hang_exercise(self):
        """ Run a timer based hang exercise. """
        # Hang exercise
        t = threading.currentThread()
        self.exercise_t = 0
        self.sensors.run_one_measure()
        self._assert_somebody_hanging() #FIXME
        while (float(self.exercise_t) < float(self.exercise_t1 - self.epsilon)):
            time.sleep (self.exercise_dt)
            self.exercise_t = self.exercise_t + self.exercise_dt
            self.exercise_rest = self.exercise_t1 - self.exercise_t
            self.exercise_completed = float(self.exercise_t) / float(self.exercise_t1) *100
            self.sensors.run_one_measure()
            #print ("%f of %f (%f percent) completed" % (self.exercise_t, self.exercise_t1, self.exercise_completed))
            self.assemble_message_exercise_timerstatus()
            if (self.sensors.Changed == "NoHang"):
                break
            if (getattr(t, "do_stop", False)):                
                break

    def run_pause_exercise(self):
        """ Run a pause after an exercise in a set. """
        # Pause exercise
        t = threading.currentThread()
        self.exercise_t = 0
        self.sensors.run_one_measure()
        self._assert_nobody_hanging() #FIXME
        while (float(self.exercise_t) < float(self.pause - self.epsilon)):
            time.sleep (self.exercise_dt)
            self.exercise_t = self.exercise_t + self.exercise_dt
            self.exercise_rest = self.pause - self.exercise_t
            self.exercise_completed = float(self.exercise_t) / float(self.pause) *100
            self.sensors.run_one_measure()
            #print ("%d of %d (%f percent) pause." % (self.exercise_t, self.pause, self.exercise_completed)) 
            self.assemble_message_pause_timerstatus()
            if (self.sensors.Changed == "Hang"):
                break
            if (getattr(t, "do_stop", False)):                
                break

    def run_set(self):
        """ Run a set in a workout. """
        logging.debug('Run exercise')

        self.__get_current_set()
        
        # Counter variables 
        self.exercise_t0 = 0
        self.exercise_t1 = self.counter
        self.exercise_t = 0
        self.exercise_rest = self.counter
        self.exercise_completed = 0

        # Rest to start loop
        self.epsilon = 0.0001
        self._assert_nobody_hanging() #FIXME
        self.run_rest_to_start()

        # Set loop
        self.rep_current = 0
        logging.debug("Set loop")
        for self.rep_current in range (0, self.reps):
            print ("%d of %d reps: %s for %d on left %s and right %s with pause of %d" % (self.rep_current, self.reps, self.type, self.counter, self.left, self.right, self.pause)) 
            self.run_hang_exercise()
  
            # Pause after exercise
            self.run_pause_exercise()

    def assemble_message_exercise_timerstatus(self):
        # FIXME: hide this function call
        als = self.sensors.sensor_hangdetector._load_series
        ats = self.sensors.sensor_hangdetector._time_series
        msg = json.dumps({"Exercise": self.exercise, "Type": self.type, "Left": self.left, "Right": self.right, 
            "Counter": "{:.2f}".format(self.counter), "CurrentCounter": "{:.2f}".format(self.exercise_t), "Completed": "{:.0f}".format(self.exercise_completed), "Rest": "{:.2f}".format(self.exercise_rest),
            "HangChangeDetected": self.sensors.Changed, "HangDetected": self.sensors.HangDetected,
            "FTI": self.sensors.FTI, "AverageLoad": self.sensors.AverageLoad, "MaximalLoad": self.sensors.MaximalLoad, "RFD": self.sensors.RFD, "LoadLoss": self.sensors.LoadLoss,
            "CurrentMeasurementsSeries": {"time": ats, "load": als}
            })
            
        print (msg)
        sys.stdout.flush()
        self.message = msg
        return (msg)

    def assemble_message_pause_timerstatus(self):
        msg = json.dumps({"Exercise": "Pause", "Type": "Pause", "Left": "", "Right": "", 
            "Counter": "{:.2f}".format(self.pause), "CurrentCounter": "{:.2f}".format(self.exercise_t), "Completed": "{:.0f}".format(self.exercise_completed), "Rest": "{:.2f}".format(self.exercise_rest),
            "HangChangeDetected": self.sensors.Changed, "HangDetected": self.sensors.HangDetected})
        print (msg)
        sys.stdout.flush()
        self.message = msg
        return (msg)        

    def assemble_message_nothing(self):
        # FIXME: instead of hard numbers - set variables
        msg = json.dumps({"Exercise": "Pause", "Type": "Pause", "Left": "", "Right": "", 
            "Counter": 0.0, "CurrentCounter": 0.0, "Completed": 0.0, "Rest": 0.0,
            "HangChangeDetected": self.sensors.Changed, "HangDetected": self.sensors.HangDetected})
        print (msg)
        sys.stdout.flush()
        self.message = msg
        return (msg) 

    def assemble_message_resttostart_timerstatus(self):
        msg = json.dumps({"Exercise": "Pause", "Type": "Rest to start", "Left": "", "Right": "", 
            "Counter": "{:.2f}".format(self.rest_to_start), "CurrentCounter": "{:.2f}".format(self.exercise_t), "Completed": "{:.0f}".format(self.exercise_completed), "Rest": "{:.2f}".format(self.exercise_rest),
            "HangChangeDetected": self.sensors.Changed, "HangDetected": self.sensors.HangDetected})
        print (msg)
        sys.stdout.flush()
        self.message = msg
        return (msg)        

    def _run_workout (self):
        """ Start a workout "run" in a thread. """
        self.message = json.dumps({"CommandResponse": "Start: Ok"})
        if (not self._workout_running):
            logging.debug("No Workout running - start one")
            self._workout_running = True
            self.run_workout_thread = threading.Thread(target=self.run_workout)
            self.run_workout_thread.do_stop = False
            self.run_workout_thread.start()     
        else:
            logging.debug("Workout running - do not start a new one")



    def _stop_workout (self):
        """ Stop a workout "run" thread" by setting a flag, which must be caputured in "run_set". """
        self.message = json.dumps({"CommandResponse": "Stop: Ok"})
        if (self._workout_running):
            logging.debug("Workout running - stop it")
            self._workout_running = False
            self.run_workout_thread.do_stop = True
            self.assemble_message_nothing()
            #self.run_workout_thread.join()
        else:
            logging.debug("No Workout running - nothing to stop")


    def _get_current_measurements_series(self):
        """ Obtain the current measurement time series from sensors.""" 
        # TODO implement 
        als = self.sensors.sensor_hangdetector._load_series
        ats = self.sensors.sensor_hangdetector._time_series
        list = json.dumps({"CurrentMeasurementsSeries": {"time": ats, "load": als}})
        return list
        

""" Main loop only for testing purposes. """
if __name__ == "__main__":
    print ("Starting")
    wa = Workout()
    #wa.run_workout()
    #wa._run_workout()
    #wa.run_websocket_handler()       
    a = wa._calc_time_in_current_workout()   
    print (a)      