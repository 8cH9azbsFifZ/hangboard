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
from counter import Counter


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
        if msg.payload.decode() == "ListWorkouts":
            self._list_workouts()

     

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
        #logging.debug("List workouts")
        workout_array = []
        
        for filename in os.listdir (self.workoutdir):
            if filename.endswith ("json"):
                fn = os.path.join(self.workoutdir, filename)
                with open(fn) as json_file:
                    data = json.load(json_file)

                    for workout in (data["Workouts"]):
                        logging.debug (workout["Name"], fn)
                        workout_array.append({"Name": workout["Name"], "ID": workout["ID"]})
        #logging.debug (workout_array)
        msg = json.dumps({"WorkoutList": workout_array})
        self._sendmessage("/workoutlist", msg)


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

    wa = Workout(hostname="hangboard")
    #wa.run_workout()
    #wa._run_workout()
    #wa.run_websocket_handler()   
    # cf. http://www.steves-internet-guide.com/loop-python-mqtt-client/
    #wa._client.loop_forever()   
    #wa._client.loop_start()   
    wa._core_loop()

    a = wa._calc_time_in_current_workout()   
    #wa._run_workout()
