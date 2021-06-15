
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
                    format='Sensors(%(threadName)-10s) %(message)s',
                    )


from sensor_zlagboard import SensorZlagboard
from sensor_force import SensorForce




class Sensors(): # FIXME: move to separate file
    def __init__(self, hangdetector = "Force", sampling_interval = 0.01):
        
        # Hang State
        self.HangDetected = False
        self.Changed = "" # Can be "Hang" or "NoHang"
        self.HangHasBegun = False
        self.HangHasStopped = False

        # Hang Duration
        self.LastHangTime = 0
        self.LastPauseTime = 0
        self._TimeStateChangeCurrent = time.time()       
        self._TimeStateChangePrevious = self._TimeStateChangeCurrent

        self._sampling_interval = sampling_interval
        self._hangdetector = hangdetector # "Force" or "Zlagboard"

        # Calculated Values
        self.FTI = 0
        self.AverageLoad = 0
        self.MaximalLoad = 0
        self.RFD = 0
        self.LoadLoss = 0

        self._init_sensors()


    def _init_sensors(self):
        if (self._hangdetector == "Force"):
            logging.debug("Hangdetector: force")
            self.sensor_hangdetector = SensorForce(sampling_interval = self._sampling_interval)
        if (self._hangdetector == "Zlagboard"):
            logging.debug("Hangdetector: zlagboard")
            self.sensor_hangdetector = SensorZlagboard(sampling_interval = self._sampling_interval)        

    def run_one_measure(self):
        self._TimeStateChangePrevious = self._TimeStateChangeCurrent
        self._TimeStateChangeCurrent = time.time()

        self.sensor_hangdetector.run_one_measure()
        
        self._detect_hang_state_change()
        self._measure_hangtime()
        self._measure_additional_parameters()

    def _measure_additional_parameters(self):
        if (self._hangdetector == "Force"):
            self.FTI = self.sensor_hangdetector.FTI
            self.AverageLoad = self.sensor_hangdetector.AverageLoad
            self.MaximalLoad = self.sensor_hangdetector.MaximalLoad
            self.RFD = self.sensor_hangdetector.RFD
            self.LoadLoss = self.sensor_hangdetector.LoadLoss

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

    def _calc_DutyCycle(self): # TODO implement
        """
        // DutyCycle calculate the percentage of time doing force vs resting
        // It decides when it's "on" and when "off" based on the StrengthStartThreshold
        """