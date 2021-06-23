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
from types import TracebackType

import paho.mqtt.client as mqtt

"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Workout(%(threadName)-10s) %(message)s',
                    )

from board import Board
from sensors import Sensors

class Counter():
    def __init__(self, workout, hostname="localhost", port=1883):
        self.workout = workout
        self._index = 0
        self._current_set = 0
        self._current_rep = 0
        self._current_set_counter = 0
        self._current_exercise_type = ""
        
        # MQTT connection handling
        self._client = mqtt.Client()
        self._client.connect(hostname, port,60)

        # Board configuration for hold setup
        self._board = Board()
        self.HoldSetup = ""
        
        # Get all general information
        self._total_sets = len (self.workout["Sets"])

        # Get information on the first set
        self._get_current_set()

        # Internal timer start and stop times
        self._tstart = 0
        self._tstop = 0

        # External timer state variables
        self.TimeElapsed = 0
        self.TimeDuration = 0
        self.TimeCompleted = 0
        self.TimeRemaining = 0
        self._lastcountdown = 0
        self.TimeCountdown = 0

    def _get_current_set(self):
        self._resttostart = self.workout["Sets"][self._current_set]["Rest-to-Start"]
        self._pause = self.workout["Sets"][self._current_set]["Pause"]
        self._reps = self.workout["Sets"][self._current_set]["Reps"]
        self._counter = self.workout["Sets"][self._current_set]["Counter"]
        self._exercise = self.workout["Sets"][self._current_set]["Exercise"]
        self._current_set_total = 1 + self._reps * 2 # rest to start and #reps exercises and pauses

        holdtypeleft = self.workout["Sets"][self._current_set]["Left"]
        holdtyperight = self.workout["Sets"][self._current_set]["Right"]
        
        self._left = self._board.get_hold_for_type(holdtypeleft)[0]
        self._right = self._board.get_hold_for_type(holdtyperight)[-1]

    def __iter__(self):
        return self

    def __next__(self):
        # Get the indices right

        # Iterate through workout
        if self._current_set < self._total_sets:
            # Iterate through rest-to-start 
            if self._current_set_counter == 0:
                self._current_exercise_type = "Rest to start"
                self._current_set_counter = self._current_set_counter + 1 # count initial "rest to start" as iteration "0"
            # Iterate though exercises and pauses
            elif self._current_set_counter <= self._reps:
                if self._current_exercise_type == "Pause": # Pause always after exercise of any type or "rest to start"
                    self._current_set_counter = self._current_set_counter + 1
                    self._current_exercise_type = self._exercise
                else:
                    self._current_exercise_type = "Pause" # After any exericse: a pause
            # Interate through sets
            else: 
                self._current_set = self._current_set + 1
                self._get_current_set()
                self._current_set_counter = 0
            self._index = self._index + 1
        else:
            raise StopIteration()

        self._get_current_hold_setup()
        self._start_current_timer()

        return self._index

    def _start_current_timer(self):
        self._tstart = time.time()
        self._tstop = 0
        if (self._current_exercise_type == "Rest to start"):
            self._tstop = self._tstart + self._resttostart
            self._tduration = self._resttostart
        elif (self._current_exercise_type == "Pause"):
            self._tstop = self._tstart + self._pause
            self._tduration = self._pause
        elif (self._current_exercise_type == "Hang"):
            self._tstop = self._tstart + self._counter
            self._tduration = self._counter
        else:
            self._tstart = 0
            self._tduration = 0

    def _get_current_hold_setup(self):
        if (self._current_exercise_type == "Rest to start"):
            self.HoldSetup = '{"Left": "", "Right": ""}'
        elif (self._current_exercise_type == "Pause"):
            self.HoldSetup = '{"Left": "", "Right": ""}'
        elif (self._current_exercise_type == "Hang"):
           self.HoldSetup = '{"Left": "' + self._left + '", "Right": "' + self._right + '"}'
        else:
            self.HoldSetup = '{"Left": "' + self._left + '", "Right": "' + self._right + '"}'

        self._sendmessage("/holds", self.HoldSetup)
        self._sendmessage("/exercisetype", '"'+self._current_exercise_type+'"') # FIXME: put somewhere else?

    def get_current_timer_state(self):
        if self._tstart > 0:
            time_current = time.time()
            self.TimeElapsed = time_current - self._tstart
            self.TimeDuration = self._tduration
            self.TimeCompleted = self.TimeElapsed / self.TimeDuration
            self.TimeRemaining = self.TimeDuration - self.TimeElapsed
            (current_remaining_full_second, current_remaining_full_second_decimals) = divmod(self.TimeRemaining + 1,1)
            if self._lastcountdown != current_remaining_full_second:
                self._lastcountdown = current_remaining_full_second
                self.TimeCountdown = current_remaining_full_second
            else:
                self.TimeCountdown = -1
        else:
            self.TimeElapsed = 0
            self.TimeDuration = 0
            self.TimeCompleted = 0
            self.TimeRemaining = 0

        self._timerstatus = '{"Duration": '+"{:.2f}".format(self.TimeDuration) +', "Elapsed":'+"{:.2f}".format(self.TimeElapsed) +', "Completed": '+"{:.2f}".format(self.TimeCompleted)+', "Countdown": ' + str(self.TimeCountdown) + '}'
        self._sendmessage("/timerstatus", self._timerstatus)

        return self.TimeElapsed > self.TimeDuration

    def _sendmessage(self, topic="/none", message="None"):
        ttopic = "hangboard/workout"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self._client.publish(ttopic, mmessage)


class Workout():
    """
    All stuff for handling workouts containing sets of exercises.
    """
    def __init__(self, verbose=None, dt=0.1, workoutdir="../exercises/workouts", workoutfile="workout-test.json",
        hostname="localhost", port=1883):
        self._hostname = hostname
        self.workoutdir = workoutdir
        self.select_workout(workoutdir + "/" + workoutfile)
        self.exercise_status = "Status"
        self.workout_number = 0
        self.workout = (self._data["Workouts"][self.workout_number])
        self.workout_name = self.workout["Name"]
        self.total_sets = len (self.workout["Sets"])
        self.current_set = 0
        self.current_set_name = "Rest to start"
        self.current_set_state = "Set" # or Pause
        self.current_rep_state = "Exercise" # or Pause
        self.sampling_interval = dt
        self._timer_max = 0 # maximal timer for core loop

        # Variable to check if ready or somebody hanging
        self.exercise_hanging = False

        self.exercise_dt = dt

        # Variable storing the message for the "middleware" -> Sending
        self.message = ""

        # State of the current workout
        self._workout_running = False

        # Connect to MQTT
        self._client = mqtt.Client()

        #self._client1 = mqtt.Client()
        #self._client1.connect(hostname, port,60)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(hostname, port,60)
        self._sendmessage("/status", "Starting")

        self.board = Board()
        self.sensors = Sensors(hostname=hostname)

        self._counter = Counter(self.workout, hostname=hostname)

    def _sendmessage(self, topic="/none", message="None"):
        ttopic = "hangboard/workout"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self._client.publish(ttopic, mmessage)

    def _on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self._client.subscribe("hangboard/workout/control")

    def _on_message(self, client, userdata, msg):
        """ Start with 
        mosquitto_pub -h localhost -t hangboard/workout/control -m Start
         Start
        """
        logging.debug(">MQTT: " + msg.payload.decode())
        if msg.payload.decode() == "Stop":
            #time.sleep(10)
            self._workout_running = False
            #exit()
        if msg.payload.decode() == "Start":
            self._workout_running = True
            next(self._counter)
        if msg.payload.decode() == "Restart":
            self._workout_running = True
            self._counter = Counter(self.workout, hostname=self._hostname)

     

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


    def _get_current_measurements_series(self):
        """ Obtain the current measurement time series from sensors.""" 
        # TODO implement 
        als = self.sensors.sensor_hangdetector._load_series
        ats = self.sensors.sensor_hangdetector._time_series
        list = json.dumps({"CurrentMeasurementsSeries": {"time": ats, "load": als}})
        return list

    def _select_next_exercise(self):
        """ Increase set and rep counter if possible and return whether it has been possible"""
        if self.current_rep < self.workout["Sets"][self.current_set]["Reps"] - 1:
            self.current_rep = self.current_rep + 1
        else:
            self.current_rep = 0
            if self.current_set < len (self.workout["Sets"]) - 1:
                self.current_set = self.current_set + 1
            else:
                return False
        return True


    def _core_loop(self):
        # https://stackoverflow.com/questions/46832084/python-mqtt-reset-timer-after-received-a-message
        # cf. http://www.steves-internet-guide.com/loop-python-mqtt-client/
        samplingrate = 0.01

        while True:

            self._client.loop(samplingrate) #blocks for 100ms (or whatever variable given, default 1s)
            if not self._workout_running: # flag for a running workout :>
                continue 
                
            self.sensors.run_one_measure()
            timer_done = self._counter.get_current_timer_state()
            if timer_done:
                next(self._counter)
            # TODO - if no hang quit it
            # TODO - start hang counter only on hang

          

      


""" Main loop only for testing purposes. """
if __name__ == "__main__":
    print ("Starting")

    wa = Workout(hostname="t20")
    #wa.run_workout()
    #wa._run_workout()
    #wa.run_websocket_handler()   
    # cf. http://www.steves-internet-guide.com/loop-python-mqtt-client/
    #wa._client.loop_forever()   
    #wa._client.loop_start()   
    wa._core_loop()

    a = wa._calc_time_in_current_workout()   
    #wa._run_workout()
