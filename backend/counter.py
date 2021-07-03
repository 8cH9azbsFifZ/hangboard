"""
Class containing the central counter for the hangboard application.
"""

import time

from types import TracebackType
import json

import paho.mqtt.client as mqtt

"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Counter(%(threadName)-10s) %(message)s',
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
        self._exercise_list = ""

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



    def _get_current_set(self, index=0):
        i = self._current_set + index
        if i >= self._total_sets:
            return 

        self._resttostart = self.workout["Sets"][i]["Rest-to-Start"]
        self._pause = self.workout["Sets"][i]["Pause"]
        self._reps = self.workout["Sets"][i]["Reps"]
        self._counter = self.workout["Sets"][i]["Counter"]
        self._exercise = self.workout["Sets"][i]["Exercise"]
        self._current_set_total = 1 + self._reps * 2 # rest to start and #reps exercises and pauses

        self._holdtypeleft = self.workout["Sets"][i]["Left"]
        self._holdtyperight = self.workout["Sets"][i]["Right"]
        
        self._left = self._board.get_hold_for_type(self._holdtypeleft)[0] # FIXME: what if no suitable holds found?
        self._right = self._board.get_hold_for_type(self._holdtyperight)[-1]

        self._intensity = 1 
        if "Intensity" in self.workout["Sets"][i]: # FIXME: must alway be given?
            self._intensity = "%.1f" % self.workout["Sets"][i]["Intensity"]

        self._type = self.workout["Sets"][i]["Type"] # FIXME: always defined?

        self._sendmessage("/setinfo", '{"resttostart": '+str(self._resttostart)+', "exercise": "'+self._exercise+'", "counter": '+str(self._counter)+', "pause": '+str(self._pause)+', "reps": '+str(self._reps)+', "left": "'+self._left+'", "right": "'+self._right+'", "type": "'+self._current_exercise_type+'", "intensity": '+str(self._intensity)+'}')

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
                if self._current_exercise_type == "Pause" or self._current_exercise_type == "Rest to start": # Pause always after exercise of any type or "rest to start"
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
        self._publish_exercise()
        self._start_current_timer()

        return self._index

    def _show_upcoming_exercise(self):
        self._get_current_set(index=0) # FIXME: index can leave
        self._get_current_hold_setup(upcoming=True)
        self._publish_exercise()

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
        elif (self._current_exercise_type == "1 Hand Pull"):
            self._tstop = self._tstart + self._counter
            self._tduration = self._counter
        else:
            self._tstart = 0
            self._tduration = 0

    def _get_current_hold_setup(self, upcoming = False):
        if (self._current_exercise_type == "Rest to start"):
            self.HoldSetup = '{"Left": "", "Right": ""}'
        elif (self._current_exercise_type == "Pause"):
            self.HoldSetup = '{"Left": "", "Right": ""}'
        elif (self._current_exercise_type == "Hang"):
            self.HoldSetup = '{"Left": "' + self._left + '", "Right": "' + self._right + '"}'
        else:
            self.HoldSetup = '{"Left": "' + self._left + '", "Right": "' + self._right + '"}'

        if upcoming:
            self.HoldSetup = '{"Left": "' + self._left + '", "Right": "' + self._right + '"}'


    def _publish_exercise(self):
        self._sendmessage("/holds", self.HoldSetup)
        self._sendmessage("/exercisetype", '"'+self._current_exercise_type+'"')

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

        if self.TimeCountdown >= 0:
            self._timerstatus = '{"Duration": '+"{:.2f}".format(self.TimeDuration) +', "Elapsed":'+"{:.2f}".format(self.TimeElapsed) +', "Completed": '+"{:.2f}".format(self.TimeCompleted)+', "Countdown": ' + str(self.TimeCountdown) + '}'
            self._sendmessage("/timerstatus", self._timerstatus)

        return self.TimeElapsed > self.TimeDuration


    def _sendmessage(self, topic="/none", message="None"):
        ttopic = "hangboard/workout"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self._client.publish(ttopic, mmessage)


    def _calc_time_in_current_workout(self): # FIXME other name
        """
        Caluculate total time, estimated rest time and planned time in this workout so far
        Create a string with remianing exercises in the form: 5x 10s Hang on 15mm, 180s rest
        """
        # FIXME: run after every counter++

        total_time = 0
        estimated_rest_time = 0
        planned_time_sofar = 0

        self._exercise_list = ""

        for s in range (0, self._total_sets-1): 
            resttostart = self.workout["Sets"][s]["Rest-to-Start"]
            pause = self.workout["Sets"][s]["Pause"]
            reps = self.workout["Sets"][s]["Reps"]
            counter = self.workout["Sets"][s]["Counter"]
            exercise = self.workout["Sets"][s]["Exercise"]
            holdtypeleft = self.workout["Sets"][s]["Left"]
            holdtyperight = self.workout["Sets"][s]["Right"]

            exercisetype = self.workout["Sets"][s]["Type"]

            intensity = None 
            if "Intensity" in self.workout["Sets"][s]:
                intensity = " I=" + "%.1f" % self.workout["Sets"][s]["Intensity"]

            # FIXME: left / right
            # FIXME: pull up without seconds

            # Select hand for 1 handed exercise
            hand = " @" + holdtyperight
            if holdtypeleft == "":
                hand = " rh @" + holdtyperight
            if holdtyperight == "":
                hand = " lh @" + holdtypeleft

            # Set hang duration or count (pull ups)
            rr = ""
            if exercisetype == "Hang": # FIXME: Max hang 
                rr = str(counter) + "s "
            elif exercisetype == "1 Hand Pull":
                rr = str(counter) + "s "
            else:
                rr = str(counter) + " " # FIXME: max pullups

            # Intensity if applicable
            ii = ""
            if intensity != None:
                ii = intensity

            # Pause notation
            pp = " & " + str(pause) + "s pause." 

            # display only upcoming sets:
            if self._current_set <= s:
                self._exercise_list = self._exercise_list + '\\n' + str(reps) + "x " + rr + exercise + hand + ii + pp

            settime = resttostart + reps * (counter + pause)
            if (self._current_set >= s): 
                planned_time_sofar = planned_time_sofar + settime
            total_time = total_time + settime

        #logging.debug(self._exercise_list)

        estimated_rest_time = total_time - planned_time_sofar

        self._sendmessage("/upcoming", '{"UpcomingSets": "' + self._exercise_list + '", "RemainingTime": ' + str(estimated_rest_time) + '}')

        return [total_time, planned_time_sofar, estimated_rest_time] # FIXME do not return

