"""
File containing all workout related classes.

This is the new thread based implementation of the classes.
Lessons learned: Microservices are fine, but nanoservices not :)
"""

import json
import os
import time
import sys

import paho.mqtt.client as mqtt

"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG, format='Workout(%(threadName)-10s) %(message)s',)

sys.path.append('../../boards')
from board import Board

sys.path.append('../sensor-force')

from counter import Counter


class Workout():
    """
    All stuff for handling workouts containing sets of exercises.
    """
    def __init__(self, verbose=None, dt=0.1, workoutdir="../../exercises/workouts", workoutfile="workout-test.json", # FIXME
        workout_id="ZB-A-1", hostname="localhost", port=1883):

        self._hostname = hostname
        self.exercise_status = "Status" # FIXME: this could leave

        ## Set counter variable: Which set is currently active (serves as index)
        self.current_set = 0
        ## Name of the current set
        self.current_set_name = "Rest to start"
        ## Status of the current set: "Set" or "Pause"
        self.current_set_state = "Set" #FIXME: can leave
        ## Status of the current repetition: "Exercise" or "Pause"
        self.current_rep_state = "Exercise" 
        ## Sampling interval for the main counter loop 
        self.sampling_interval = dt
        ## Maximal timer for the core loop
        self._timer_max = 0 # FIXME: can leave

        ## Variable to check if ready or somebody hanging
        self.exercise_hanging = False

        self.exercise_dt = dt # FIXME with sampling interval

        ## Variable storing the message for the "middleware" -> Sending
        self.message = "" # FIXME: can leave

        # State of the current workout
        self._workout_running = False

        # Connect to MQTT
        self._client = mqtt.Client("Workout")

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(hostname, port,60)
        self._sendmessage("/status", "Starting")

        ## Handle the current board setup (Instance of class Board) 
        #self.board = Board()                                      

        # Variables for workout selection
        self._workoutdir = workoutdir
        self._workoutfile = ""
        self._workout_number = 0 
        self._workout = {} 
        self._workout_name = ""
        self._workoutlist = []
        ## Number of total sets in the current workout
        self.total_sets = 0
        self._set_workout(workout_id) # TODO - implement MQTT command #59

        self._HangDetected = False

        # Configure User
        # self._dbhost="hangboard" # FIXME
        # self._dbuser="root"
        # self._dbpassword="rootpassword"
        # self._set_user("us3r")


    def _sendmessage(self, topic="/none", message="None"):
        """ Send a message using MQTT """
        ttopic = "hangboard/workout"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self._client.publish(ttopic, mmessage)

    def _on_connect(self, client, userdata, flags, rc):
        """ Connect to MQTT broker and subscribe to control messages """
        print("Connected with result code "+str(rc))
        self._client.subscribe("hangboard/workout/control")
        self._client.subscribe("hangboard/sensor/load/loadstatus")


    def _on_message(self, client, userdata, msg):
        """ 
        Receive MQTT control messages.
        Start with debugging on commandline using:
        mosquitto_pub -h localhost -t hangboard/workout/control -m Start
        """
        logging.debug(">MQTT: " + msg.payload.decode())
        
        # Controls
        if msg.topic == "hangboard/workout/control":
            if msg.payload.decode() == "Stop":
                #time.sleep(10)
                self._workout_running = False
                #exit()
            if msg.payload.decode() == "Start":
                self._workout_running = True
                next(self._counter)
            if msg.payload.decode() == "Restart":
                self._workout_running = True
                self._counter = Counter(self._workout, hostname=self._hostname)
            if msg.payload.decode() == "ListWorkouts":
                self._list_workouts()

        # Hang data
        if msg.topic == "hangboard/sensor/load/loadstatus":
            jj = json.loads(msg.payload.decode())
            if jj["HangDetected"] == "True":
                self._HangDetected = True
            else:
                self._HangDetected = False
            return


     

    def select_workout(self, filename):
        """ Select a workout based on a filename. """
        self._workoutfile = filename # FIXME
        self.filename = self._workoutfile

    def _get_current_workout(self):
        """
        Print the total current workout and it in the messaging queue (self.message)
        """
        logging.debug("Get current workout")
        self.message = json.dumps({"CurrentWorkout": self._data})

    def _list_workouts(self):
        """
        Get list of available workouts and put it in the messaging queue (self.message)
        """
        #logging.debug("List workouts")
        workout_array = []
        
        for filename in os.listdir (self._workoutdir):
            if filename.endswith ("json"):
                fn = os.path.join(self._workoutdir, filename)
                with open(fn) as json_file:
                    data = json.load(json_file)

                    i = 0
                    tt = time.time()
                    for workout in (data["Workouts"]):
                        logging.debug (workout["Name"], fn)
                        workout_array.append({"Name": workout["Name"], "ID": workout["ID"], "Filename": fn , "IndexInFile": i, "Time": tt})
                        i = i + 1
        #logging.debug (workout_array)
        self._workoutlist = workout_array
        msg = json.dumps({"WorkoutList": workout_array})
        self._sendmessage("/workoutlist", msg)
        return (workout_array)

    def run_workout (self): # FIXME delete
        """
        Run a single workout
        """
        logging.debug("Running workout")
        for self.current_set in range (0, self.total_sets):
            self.run_set()


    def _core_loop(self):
        """
        This is the core workout loop. 
        A description of the chosen design can be found here
        https://stackoverflow.com/questions/46832084/python-mqtt-reset-timer-after-received-a-message
        and here
        http://www.steves-internet-guide.com/loop-python-mqtt-client/
        """
        samplingrate = 0.01

        self._counter._show_upcoming_exercise()

        while True:

            self._client.loop(samplingrate) #blocks for 100ms (or whatever variable given, default 1s)
            
            if not self._workout_running: # flag for a running workout :>
                continue 

            upcoming = self._counter._show_upcoming_exercise()
            print (upcoming)
                
            #self.sensors.run_one_measure() # FIXME: implicit run - connect to MQTT(!)
            #self._update_user_statistics() 
            timer_done = self._counter.get_current_timer_state()
            self._counter._calc_time_in_current_workout()
            if timer_done:
                # Start next timer only when hang detected for "not pause" exercises -> means next is a hang
                if self._counter._current_exercise_type == "Pause" or self._counter._current_exercise_type == "Rest to start":
                    if self._HangDetected:
                        next(self._counter)
                    else:
                        # show at least upcoming config
                        self._counter._show_upcoming_exercise() 
                        # FIXME: last exercise i.e. self._current_set < self._total_sets
                # Start next timer only when np hang detected if currently no pause -> means next is a pause
                else:
                    if not self._HangDetected:
                        next(self._counter)
            # Next timer if a "not pause" exercise is combined with "no hang" -> means exercise aborted
            if not (self._counter._current_exercise_type == "Pause" or self._counter._current_exercise_type == "Rest to start"):
                if not self._HangDetected:
                    next(self._counter)

    def _set_workout (self, id="ZB-A-1"):      
        """ Set current workout for the timer """
        logging.debug ("Select workout: " + id)
        index = -1
        if self._workoutlist == []:
            self._list_workouts()     

        for i in range(0,len(self._workoutlist)-1):
            if self._workoutlist[i]["ID"] == id:
                index = i
                break
        
        if i == -1: # Exercise not found
            logging.debug ("Workout not found")
            return -1

        self._workoutfile = self._workoutlist[index]["Filename"]
        self._workout_number = self._workoutlist[index]["IndexInFile"]
        self._workout_name = self._workoutlist[index]["Name"]
        self._workout_id = id

        logging.debug ("Selecting workout: " + str(self._workoutlist[index]))

        # Read workout file
        with open(self._workoutfile) as json_file:
            self._data = json.load(json_file)
        self._workout = (self._data["Workouts"][self._workout_number])
        self.total_sets = len (self._workout["Sets"])


        # Initialize new counter
        self._counter = Counter(self._workout, hostname=self._hostname)

        # Communicate on currently selected workout
        self._sendmessage("/workoutstatus", json.dumps(self._workoutlist[index]))

    def workout2html(self):
        
        while True:    
            upcoming = self._counter._show_upcoming_exercise()
            print (upcoming)
            i1 = next(self._counter)
            if i1 == -1:
                return
           

""" Main loop only for testing purposes. """
if __name__ == "__main__":
    print ("Starting")

    wa = Workout(hostname="localhost")

    #wa._set_workout(id="HRST-S-1-4ZBEVO")
    list_wa = wa._list_workouts()
    #print (list_wa)
    wa._set_workout(id="BEASTY-5A")
    total_time = wa._counter._calc_time_in_current_workout()
    print ("total_time, planned_time_sofar, estimated_rest_time",total_time)

    wa.workout2html()
