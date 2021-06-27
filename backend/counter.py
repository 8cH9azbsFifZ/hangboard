"""
Class containing the central counter for the hangboard application.
"""

import time

from types import TracebackType

import paho.mqtt.client as mqtt

"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Counter(%(threadName)-10s) %(message)s',
                    )


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

        if self.TimeCountdown >= 0:
            self._timerstatus = '{"Duration": '+"{:.2f}".format(self.TimeDuration) +', "Elapsed":'+"{:.2f}".format(self.TimeElapsed) +', "Completed": '+"{:.2f}".format(self.TimeCompleted)+', "Countdown": ' + str(self.TimeCountdown) + '}'
            self._sendmessage("/timerstatus", self._timerstatus)

        return self.TimeElapsed > self.TimeDuration


    def _sendmessage(self, topic="/none", message="None"):
        ttopic = "hangboard/workout"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self._client.publish(ttopic, mmessage)
