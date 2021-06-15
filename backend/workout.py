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


from sensor_zlagboard import SensorZlagboard
from sensor_force import SensorForce

from board import Board


class Sensors(): # FIXME: move to separate file
    def __init__(self, hangdetector = "Force", sampling_interval = 0.01):
        

        self.HangDetected = False
        self.Changed = "" # Can be "Hang" or "NoHang"
        self.HangHasBegun = False
        self.HangHasStopped = False

        self.LastHangTime = 0
        self.LastPauseTime = 0
        self._TimeStateChangeCurrent = time.time()       
        self._TimeStateChangePrevious = self._TimeStateChangeCurrent

        self._sampling_interval = sampling_interval
        self._hangdetector = hangdetector # "Force" or "Zlagboard"

        self.init_sensors()


    def init_sensors(self):
        if (self._hangdetector == "Force"):
            self.sensor_hangdetector = SensorForce(sampling_interval = self._sampling_interval)
        if (self._hangdetector == "Zlagboard"):
            self.sensor_hangdetector = SensorZlagboard(sampling_interval = self._sampling_interval)        

    def assert_somebody_hanging(self):
        pass
        # TODO  - implement
        #while ((self.sensor_zlagboard.NobodyHanging() == True)):
        #    time.sleep (self.exercise_dt)

    def assert_nobody_hanging(self):
        pass
        # TODO implement
        #logging.debug ("Assert nobody hanging")
        #while (not (self.sensor_zlagboard.NobodyHanging() == True)):
        #    time.sleep (self.exercise_dt)

    def run_one_measure(self):
        self._TimeStateChangePrevious = self._TimeStateChangeCurrent
        self._TimeStateChangeCurrent = time.time()

        self.sensor_hangdetector.run_one_measure()

        self._detect_hang_state_change()
        self._measure_hangtime()

    def _measure_hangtime(self):
        if (self._HangStateChanged):
            if (self.HangDetected == True):
                self.LastHangTime = self._TimeStateChangeCurrent - self._TimeStateChangePrevious
            else:
                self.LastPauseTime = self._TimeStateChangeCurrent - self._TimeStateChangePrevious

    def _detect_hang_state_change(self):
        # Reset states
        self.HangHasBegun = False
        self.HangHasStopped = False
        self.Changed = ""

        # Detect state change
        oldstate = self.HangDetected
        self.HangDetected = self.sensor_hangdetector.HangDetected

        if (oldstate == self.HangDetected):
            self._HangStateChanged = False
        else:
            self._HangStateChanged = True

            if (self.HangDetected == True):
                #logging.debug ("HangStateChanged and HangDetected")
                self.HangHasBegun = True
                self.Changed = "Hang"
            else:
                self.HangHasStopped = True
                self.Changed = "NoHang"
                #logging.debug ("HangStateChanged and no HangDetected")


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
        self.sampling_interval = dt

        # Variable to check if ready or somebody hanging
        self.exercise_hanging = False

        self.exercise_dt = dt

        # Variable storing the message for the "middleware" -> Sending
        self.message = ""

        self.board = Board()
        self.sensors = Sensors()


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
        
        self.exercise_status = json.dumps({"WorkoutList": workout_array, "OneMessageOnly": True}) # FIXME

    def show_workout(self):
        print (self.data)

    def show_set(self):
        set = self.workout["Sets"][self.current_set]
        print (set)

    def show_exercise(self):
        exercise = self.workout["Sets"][self.current_set]["Exercise"]
        print (exercise)

    def run_exercise_1hand_pull(self):
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

        holdtypeleft = self.workout["Sets"][self.current_set]["Left"]
        holdtyperight = self.workout["Sets"][self.current_set]["Right"]
        
        self.left = self.board.get_hold_for_type(holdtypeleft)[0]
        self.right = self.board.get_hold_for_type(holdtyperight)[-1]

        self.counter = self.workout["Sets"][self.current_set]["Counter"]

    def _get_board_image_base64(self):
        image_base64 = self.board.svg._get_image_base64()
        print (image_base64)
        self.message = image_base64

    def run_pause(self):
        logging.debug('Run pause')



    def run_rest_to_start(self):
        logging.debug("Rest to start loop")
        t = threading.currentThread()
        self.exercise_t = 0
        self.sensors.run_one_measure()
        #self.assert_nobody_hanging() #FIXME
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
        # Hang exercise
        t = threading.currentThread()
        self.exercise_t = 0
        self.sensors.run_one_measure()
        #self.assert_somebody_hanging() #FIXME
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
        # Pause exercise
        t = threading.currentThread()
        self.exercise_t = 0
        self.sensors.run_one_measure()
        #self.assert_nobody_hanging() #FIXME
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
        #self.assert_nobody_hanging() # FIXME
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
        msg = json.dumps({"Exercise": self.exercise, "Type": self.type, "Left": self.left, "Right": self.right, 
            "Counter": "{:.2f}".format(self.counter), "CurrentCounter": "{:.2f}".format(self.exercise_t), "Completed": "{:.0f}".format(self.exercise_completed), "Rest": "{:.2f}".format(self.exercise_rest),
            "HangChangeDetected": self.sensors.Changed, "HangDetected": self.sensors.HangDetected})
            
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

    def assemble_message1(self): # TODO rework for this version
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

    def _run_workout (self):
        """
        Start a workout "set" in a thread
        """
        print ("Run thread set")
        self.run_workout_thread = threading.Thread(target=self.run_workout)
        self.run_workout_thread.do_stop = False
        self.run_workout_thread.start()           


    def _stop_workout (self):
        """
        Stop a workout "set" thread" by setting a flag, which must be caputured in "run_set".
        """
        print ("Stop thread set")
        self.run_workout_thread.do_stop = True
        self.assemble_message_nothing()
        #self.run_workout_thread.join()


if __name__ == "__main__":
    print ("Starting")
    wa = Workout()
    #wa.show_workout()
    #wa.run_workout()
    wa._run_workout()
    #wa.run_websocket_handler()                