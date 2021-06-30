"""
This class encapsulates all sensors.

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
                    format='Sensors(%(threadName)-10s) %(message)s',
                    )

import paho.mqtt.client as mqtt

from sensor_zlagboard import SensorZlagboard
from sensor_force import SensorForce

class Sensors():
    def __init__(self, hangdetector = "Force", sampling_interval = 0.01, hostname="localhost", port=1883):
        
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

        # Connect to MQTT
        self.__client = mqtt.Client()
        self.__client.connect(hostname, port,60)
        self._hostname = hostname

        self._init_sensors()

    def __sendmessage(self, topic="/none", message="None"):
        ttopic = "hangboard/sensor"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self.__client.publish(ttopic, mmessage)

    def _init_sensors(self):
        if (self._hangdetector == "Force"):
            logging.debug("Hangdetector: force")
            self.sensor_hangdetector = SensorForce(sampling_interval = self._sampling_interval, hostname=self._hostname)
        if (self._hangdetector == "Zlagboard"):
            logging.debug("Hangdetector: zlagboard")
            self.sensor_hangdetector = SensorZlagboard(sampling_interval = self._sampling_interval)        

    def run_one_measure(self):
        self._TimeCurrent = time.time()

        self.sensor_hangdetector.run_one_measure()
        
        self._detect_hang_state_change()
        self._measure_hangtime()
        self._measure_additional_parameters()
        logging.debug(" Hang load " + str(self.MaximalLoad))

        self.__sendmessage("/sensorstatus", '{"time": ' + "{:.2f}".format(self._TimeCurrent) + ', "HangChangeDetected": "' + self.Changed + '", "HangDetected": "' + str(self.HangDetected) + '"}')
        if not self.HangDetected:
            logging.debug("Last Hang load " + str(self.MaximalLoad))
            self.__sendmessage("/lastexercise", '{"LastHangTime": ' + "{:.2f}".format(self.LastHangTime) + ', "LastPauseTime": ' + "{:.2f}".format(self.LastPauseTime) + ', "MaximalLoad": ' + "{:.2f}".format(self.sensor_hangdetector.LastHang_MaximalLoad) +'}')

    def _measure_additional_parameters(self):
        if (self._hangdetector == "Force"):
            self.FTI = self.sensor_hangdetector.FTI
            self.AverageLoad = self.sensor_hangdetector.AverageLoad
            self.MaximalLoad = self.sensor_hangdetector.MaximalLoad
            self.RFD = self.sensor_hangdetector.RFD
            self.LoadLoss = self.sensor_hangdetector.LoadLoss

    def _measure_hangtime(self): # FIXME - not displayed correctly after exercise
        delta = 0
        if (self._HangStateChanged):
            self._TimeStateChangePrevious = self._TimeStateChangeCurrent
            self._TimeStateChangeCurrent = time.time()
            
            delta = self._TimeStateChangeCurrent - self._TimeStateChangePrevious

            if (self.HangDetected == True):
                self.LastPauseTime = delta
            else:
                self.LastHangTime = delta

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

    def _calc_DutyCycle(self): # TODO #77 implement
        """
        // DutyCycle calculate the percentage of time doing force vs resting
        """
        self.DutyCycle = self.LastHangTime / (self.LastHangTime+self.LastPauseTime)