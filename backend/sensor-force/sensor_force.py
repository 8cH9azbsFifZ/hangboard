"""
Force Measurement Backend
"""

"""
/*
* https://www.desnivel.com/escalada-roca/entrenamiento/analizando-la-importancia-de-la-fuerza-en-la-escalada/
* * measures:
*   - MVC: max voluntary contraction
*   - FTI: force-time integral
*   - RFD: rate of force development
* * types of workouts:
*   - MVC: for a predefined duration (7" for example), measure the strength. Metrics:
*     - average strength during the period
*     - max
*     - min
*     - deviation
*     - seconds left
*     - alarm when finished
*   - FTI, could be one serie or multiple series (repeaters)
*     - fti (integral force-time)
*     - duty cycle (percentage "on" vs "off")
*     - duration
*   - training:
*     - be able to set our MAX MCV and the percentage we want to train
*   - RFD:
*     - time to reach the max force (or 95? 99%?)
 */

"""

"""
TODO: Doc debugging:
 mosquitto_sub -h raspi-hangboard -t hangboard/sensor/load/loadstatus
 reference to interface manual:
 9azbsfifz.github.io/hangboard/api/index.html#operation-subscribe-hangboard/sensor/load/loadstatus
"""


import logging
logging.basicConfig(level=logging.DEBUG, format='SensorForce(%(threadName)-10s) %(message)s', )

import time
import sys
from scipy import integrate
from numpy import diff
import paho.mqtt.client as mqtt
import numpy as np
from scipy.ndimage.filters import uniform_filter1d
import json

import threading

from configparser import ConfigParser


EMULATE_HX711 = False #True # FIXME: parameter

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
    GPIO.setmode(GPIO.BCM) # Set PIN names to "GPIO**", such that these number correspond to the images.
    # https://raspi.tv/2013/rpi-gpio-basics-4-setting-up-rpi-gpio-numbering-systems-and-inputs

else:
    from emulated_hx711 import HX711


# FIXME: use configuration file for reference units
class SensorForce():
    def __init__(self, EMULATE_HX711 = True, 
        sampling_interval = 0.1, 
        load_hang = 2.0, # FIXME put in config file
        pin_dout1 = 17, pin_pd_sck1 = 27, referenceUnit1 = 1,
        pin_dout2 = 5, pin_pd_sck2 = 6, referenceUnit2 = 1,
        mqtt_server = "raspi-hangboard", mqtt_port = 1883): 

        logging.debug ("Initialize")

        self.pin_dout1   = pin_dout1
        self.pin_pd_sck1 = pin_pd_sck1
        self.pin_dout2   = pin_dout2
        self.pin_pd_sck2 = pin_pd_sck2

        self.referenceUnit1 = referenceUnit1
        self.referenceUnit2 = referenceUnit2

        self.sampling_rate = sampling_interval
        self.calibration_duration = 10 # FIXME: configurable

        # Threshold for detection of a hang
        self.load_hang = load_hang

        # Variables for current measurement
        self.load_current = 0
        self.time_current = time.time()
        self.load_current_balance = 0

        # Array to store 3 values to smoothen out exceptions (singular value, jumps back and forth, i.e. 0, -8.85, 0). 
        # A moving average is not correct to withdraw these values.
        # FIXME: move to hx711 lib (and push to upstream?)
        self._load3_A = [0,0,0]
        self._load3_B = [0,0,0]
        self._time3 = [0,0,0]

        # Array for storing all values
        self._load_series = []
        self._time_series = []
        self._series_max_elements = 500

       # Defined current states
        self.HangDetected = False
        self._HangStateChanged = False

        # Hang time variables
        self.LastHangTime = 0
        self.LastPauseTime = 0
        self.TimeStateChangeCurrent = self.time_current       
        self.TimeStateChangePrevious = self.TimeStateChangeCurrent

        self._Gravity = 9.80665
        # LatestValueInterval is the lenght, in ms, of the latest data stored to make som calculations
        self._LatestValueInterval = 500

        # Calculated FTI & co
        self.FTI = 0
        self.AverageLoad = 0
        self.MaximalLoad = 0
        self.RFD = 0
        self.LoadLoss = 0

        # Calculated Values for last hang
        self.LastHang_FTI = 0
        self.LastHang_AverageLoad = 0
        self.LastHang_MaximalLoad = 0
        self.LastHang_RFD = 0
        self.LastHang_LoadLoss = 0

        # Connect to MQTT
        self._client = mqtt.Client()

        self._client.connect(mqtt_server, mqtt_port, 60)
        self._sendmessage("/status", "Starting")

        self.init_hx711()
        self._sendmessage("/status", "Calibration")

        self.calibrate()

        # FIXME: do only load file as test case
        #if EMULATE_HX711:
        #    simfile = "simulation_data.json"
        #    self._simcounter = 0
        #    with open(simfile) as json_file:
        #        data = json.load(json_file)
        #    self._simdata = data["SimulationData"]

        self._moving_average_n = 3
        self._moving_average_series = []
        self._moving_average_load = 0

    def _sendmessage(self, topic="/none", message="None"):
        ttopic = "hangboard/sensor/load"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self._client.publish(ttopic, mmessage)


    def cleanAndExit(self):
        self._sendmessage("/status", "Cleanup for exit")
        self._client.disconnect()

        logging.debug("Cleaning...")
        if not EMULATE_HX711:
            GPIO.cleanup()
            
        logging.debug("Bye!")
        sys.exit()

    def init_hx711(self):
        # I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
        # Still need to figure out why does it change.
        # If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
        # There is some code below to debug and log the order of the bits and the bytes.
        # The first parameter is the order in which the bytes are used to build the "long" value.
        # The second paramter is the order of the bits inside each byte.
        # According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.

        self.hx1 = HX711(self.pin_dout1 , self.pin_pd_sck1) 
        self.hx1.set_reading_format("MSB", "MSB")
        self.hx1.set_reference_unit(self.referenceUnit1)
        self.hx1.reset()

        self.hx2 = HX711(self.pin_dout2 , self.pin_pd_sck2) 
        self.hx2.set_reading_format("MSB", "MSB")
        self.hx2.set_reference_unit (self.referenceUnit2)
        self.hx2.reset()

    def calibrate(self):
        logging.debug("Starting Tare done! Wait...")
        self._sendmessage("/status", "Starting Tare done! Wait...")

        self.hx1.tare()
        self.hx2.tare()
        
        self._sendmessage("/status", "Tare done! Add weight now...")

    # TODO implement calibrate command over MQTT  #78

    def run_main_measure(self):
        while True:
            try:
                self.run_one_measure()
                logging.debug ("Current time " + "{:.2f}".format(self.time_current)  + " load " + "{:.2f}".format(self.load_current) + " load_bal " + "{:.2f}".format(self.load_current_balance) + " average load " + "{:.2f}".format(self.AverageLoad) + " calculated FTI " + "{:.2f}".format(self.FTI)
                + " maximal load " + "{:.2f}".format(self.MaximalLoad) + " RFD " + "{:.2f}".format(self.RFD) + " LoadLoss " + "{:.2f}".format(self.LoadLoss))

                time.sleep(self.sampling_rate)

            except (KeyboardInterrupt, SystemExit):
                self.cleanAndExit()

    def _calc_moving_average(self):
        # calculate moving average
        #logging.debug("Calc moving average")
        self._moving_average_series.append(self._load_current_raw)

        if len(self._moving_average_series) > self._moving_average_n: 
            #logging.debug("Calc moving average - enough points n")
            self._moving_average_series.pop(0) # restrict size of array for moving average   
            self._moving_average_load = uniform_filter1d(self._moving_average_series, size=self._moving_average_n)
            #logging.debug("Calc moving average" + str(self._moving_average_load[self._moving_average_n-1]))
            return self._moving_average_load[self._moving_average_n-1]

        return 0

    def run_one_measure(self):
        time_current = time.time()

        # FIXME: WIRING MATTERS - ADD A COMMENT
        self._load_current_raw_A = -1*self.hx1.get_weight_A(times=1) # Never use this, but use a Low pass filter to get rid of the noise
        
        self._load_current_raw_B = -1*self.hx2.get_weight_A(times=1) # Never use this, but use a Low pass filter to get rid of the noise
        self._load_current_raw = self._load_current_raw_A  + self._load_current_raw_B 
        #logging.debug("Both channels: "+str(self._load_current_raw_A)+" and "+str(self._load_current_raw_B))


        # Fill load3 array
        accuracy = 0.01 # +/- 10g, ref: Testing out 50 kg load cells
        self._load3_A[0] = self._load3_A[1] 
        self._load3_A[1] = self._load3_A[2] 
        self._load3_A[2] = self._load_current_raw_A
        self._load3_B[0] = self._load3_B[1] 
        self._load3_B[1] = self._load3_B[2] 
        self._load3_B[2] = self._load_current_raw_B
        self._time3[0] = self._time3[1] 
        self._time3[1] = self._time3[2] 
        self._time3[2] = time_current 
        d12_A = self._load3_A[0] - self._load3_A[1] 
        d23_A = self._load3_A[1] - self._load3_A[2]
        drel_A = 0

        if abs(d12_A) > accuracy and abs(d23_A) > accuracy and d23_A is not 0:
            drel_A = d12_A/d23_A

        if drel_A + 1.0 < accuracy: # rel will yield -1.00 if value jumps up and down again - ignore previous measurement
            self._load3_A[1] = self._load3_A[2]

        d12_B = self._load3_B[0] - self._load3_B[1] 
        d23_B = self._load3_B[1] - self._load3_B[2]
        drel_B = 0

        if abs(d12_B) > accuracy and abs(d23_B) > accuracy and d23_B is not 0:
            drel_B = d12_B/d23_B

        if drel_B + 1.0 < accuracy: # rel will yield -1.00 if value jumps up and down again - ignore previous measurement
            self._load3_B[1] = self._load3_B[2]

        logging.debug("Both channels: "+f"{self._load_current_raw_A:.2f}"+" \t and "+f"{self._load_current_raw_B:.2f}"+" yields: "+f"{d12_A:.2f}"+" \t and "+f"{d23_A:.2f}"+" \t and "+f"{drel_A:.2f}")
        
        self.load_current = self._load3_A[1] + self._load3_B[1] # TODO: describe the filter
        self.load_current_balance = self._load3_A[1]
            
        self.time_current = self._time3[1] 
        # TODO: describe the load circuit hack

        #self.load_current = self._calc_moving_average() # FIXME

        if EMULATE_HX711:
            self._simcounter = self._simcounter+1
            if (self._simcounter+1 >= 100): #len(self._simdata["time"])): # FIXME does not work yet
                self._simcounter=0
            self.load_current = self._simdata["load"][self._simcounter]
            #time.sleep(0.05) # FIXME
            #logging.debug("Simulation: " + str(self._simcounter) + " load: " + str(self.load_current))

        # Hang detection
        self._detect_hang()

        # Store variables of last / current hang
        if (self.HangDetected):
            self._fill_series()
            self._Calc_FTI()
            self._Calc_RFD()
            self._calc_avg_load()
            self._calc_max_load()
            self._Calc_LoadLoss()
        else:
            self._load_series = []
            self._time_series = []

            self.LastHang_FTI = self.FTI
            self.LastHang_AverageLoad = self.AverageLoad
            self.LastHang_MaximalLoad = self.MaximalLoad
            self.LastHang_RFD = self.RFD
            self.LastHang_LoadLoss = self.LoadLoss

            self.AverageLoad = 0
            self.MaximalLoad = 0
            self.FTI = 0
            self.RFD = 0
            self.LoadLoss = 0


        #logging.debug("Sensor current max load " + str(self.MaximalLoad) + " and last maximum " + str(self.LastHang_MaximalLoad))
        self._sendmessage("/loadstatus", '{"time": ' + "{:.2f}".format(self.time_current) + ', "loadcurrent": '+ "{:.2f}".format(self.load_current) + \
            ', "loadcurrent_balance": '+ "{:.2f}".format(self.load_current_balance) + ', "loadaverage": ' + "{:.2f}".format(self.AverageLoad) + \
            ', "fti": ' + "{:.2f}".format(self.FTI) + ', "rfd": ' + "{:.2f}".format(self.RFD) + ', "loadmaximal": ' + "{:.2f}".format(self.MaximalLoad) + \
            ', "loadloss": ' + "{:.2f}".format(self.LoadLoss) + \
            ', "HangChangeDetected": "' + self.Changed + '", "HangDetected": "' + str(self.HangDetected) + '"}')
             
        if self.Changed == "NoHang":
            #logging.debug("Last Hang load " + str(self.MaximalLoad))
            self._sendmessage("/lastexercise", '{"LastHangTime": ' + "{:.2f}".format(self.LastHangTime) + ', "LastPauseTime": ' + "{:.2f}".format(self.LastPauseTime) + ', "MaximalLoad": ' + "{:.2f}".format(self.LastHang_MaximalLoad) +'}')



  

    def _calc_DutyCycle(self): # TODO #77 implement
        """
        // DutyCycle calculate the percentage of time doing force vs resting
        """
        self.DutyCycle = self.LastHangTime / (self.LastHangTime+self.LastPauseTime)
        
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

    def _calc_avg_load(self):
        avg_load = sum(self._load_series) / len (self._load_series)
        self.AverageLoad = avg_load
        return avg_load

    def _fill_series(self):
        # Cut series down to _series_max_elements
        if (len(self._load_series) > self._series_max_elements):
            self._load_series.pop(0)
            self._time_series.pop(0)

        # Fill in current value
        self._load_series.append(self.load_current)
        self._time_series.append(self.time_current)

    def _calc_max_load(self):
        if (self.load_current > self.MaximalLoad):
            self.MaximalLoad = self.load_current
        return self.MaximalLoad

    def _calc_current_intensity(self, maxload):
        """ Calculate the current intensity for a given maximal load """
        pass
        # TODO: implement #60

    def _detect_hang(self):
        # Detect state change
        oldstate = self.HangDetected

        if (self.load_current > self.load_hang):
            self.HangDetected = True
        else:
            self.HangDetected = False

        if (oldstate == self.HangDetected):
            self._HangStateChanged = False
        else:
            self._HangStateChanged = True
            if self.HangDetected:
                self.Changed = "Hang"
            else:
                self.Changed = "NoHang"

        #logging.debug("Hang detection - current load " + str(self.load_current) + " and hang threshold " + str(self.load_hang))

        return self.HangDetected


    def _calculateStart(self): # TODO measure more values and store them in advance for posthum calculations
        """
        How to detect a new exercise has started
        To get a good value for RFD and FTI we need to know the exact start time.
        The climber could load the cell while preparing or even have some load in the cell before starting
        We could store the previous 500ms of values and when we detect a high load, indicating the exercise has begin, go back in time to
        get the exact start time
        """
        pass
        
    def _calculateEnd(self): # TODO implement
        """
        calculateEnd decides when the exercise has finished, based on a big drop of force
        """
        pass

    def _Calc_FTI(self): 
        """
        FTI calculate the integral force-time from a serie of StrengthData values
        Return value is expressed in Newton*second (-> Impulse)

        return integrate.Simpsons(x, fx)      func Simpsons(x, f []float64) float64

        f[i] = f(x[i]), x[0] = a, x[len(x)-1] = b

        \int_a^b f(x)dx

        """
        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.simpson.html
        #integrate.simpson(y, x)
        # FIXME RASPI ERROR self.FTI = integrate.simpson(self._load_series, self._time_series) * self._Gravity
        return self.FTI

    def _Calc_RFD(self):
        """
        RFD the highest positive value from the first derivative of the force signal (kg/s)
        https://journals.lww.com/nsca-jscr/Fulltext/2013/02000/Differences_in_Climbing_Specific_Strength_Between.5.aspx
        FIXME: ref in docs.
        """
        rfd = 0
        if (len(self._load_series) > 2):
            derivative = diff (self._load_series) / diff(self._time_series)
            rfd = max(derivative)

        self.RFD = rfd
        return rfd

    def _Calc_LoadLoss(self):
        """
        strengthLoss is the loss of strength in percentage (0-100)   
        """
        self.LoadLoss = 1 - (self.load_current / self.MaximalLoad)
        return self.LoadLoss



if __name__ == "__main__":
    #a = SensorForce(referenceUnit = 1)


    # Read sensor configuration from file
    config_file="/home/pi/hangboard/backend/sensor-force/hangboard.ini"
    config_obj = ConfigParser()
    config_obj.read(config_file)
    sensor_force_info = config_obj["SENSOR-FORCE"]

    pin_dout1   = int(sensor_force_info["pin_dout1"])
    pin_pd_sck1 = int(sensor_force_info["pin_pd_sck1"])
    pin_dout2   = int(sensor_force_info["pin_dout2"])
    pin_pd_sck2 = int(sensor_force_info["pin_pd_sck2"])

    referenceWeight1 = float(sensor_force_info["referenceWeight1"])
    referenceValue1 = float(sensor_force_info["referenceValue1"])
    referenceUnit1 = referenceValue1/referenceWeight1

    referenceWeight2 = float(sensor_force_info["referenceWeight2"])
    referenceValue2 = float(sensor_force_info["referenceValue2"])
    referenceUnit2 = referenceValue2/referenceWeight2

    mqtt_info = config_obj["MQTT"]

    mqtt_server = mqtt_info["hostname"]
    mqtt_port = int(mqtt_info["port"])

    a = SensorForce(sampling_interval = 0.005, 
        pin_dout1 = pin_dout1, pin_pd_sck1 = pin_pd_sck1, referenceUnit1 = referenceUnit1,
        pin_dout2 = pin_dout2, pin_pd_sck2 = pin_pd_sck2, referenceUnit2 = referenceUnit2,
        mqtt_server = mqtt_server, mqtt_port = mqtt_port)

    a.run_main_measure()
