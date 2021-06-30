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


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='SensorForce(%(threadName)-10s) %(message)s',
                    )

import time
import sys
from scipy import integrate
from numpy import diff
import paho.mqtt.client as mqtt
import importlib.util
import numpy as np
from scipy.ndimage.filters import uniform_filter1d



import json

import threading

EMULATE_HX711 = False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
    GPIO.setmode(GPIO.BCM) # Set PIN names to "GPIO**", such that these number correspond to the images.
    # https://raspi.tv/2013/rpi-gpio-basics-4-setting-up-rpi-gpio-numbering-systems-and-inputs

else:
    from emulated_hx711 import HX711


class SensorForce():
    def __init__(self, EMULATE_HX711 = True, 
        pin_dout = 17, pin_pd_sck = 27, sampling_interval = 0.1, 
        referenceUnit = 1257528/79, load_hang = 2.0, # FIXME 
        hostname="localhost", port=1883): 
        logging.debug ("Initialize")

        self.pin_dout = pin_dout
        self.pin_pd_sck = pin_pd_sck

        self.referenceUnit = referenceUnit
        self.sampling_rate = sampling_interval

        self.calibration_duration = 10

        # Threshold for detection of a hang
        self.load_hang = load_hang

        # Variables for current measurement
        self.load_current = 0
        self.time_current = time.time()

        # Array for storing all values
        self._load_series = []
        self._time_series = []
        self._series_max_elements = 500

       # Defined current states
        self.HangDetected = False
        self.HangStateChanged = False

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
        self.HangStateChangedString = ""

        # Calculated Values for last hang
        self.LastHang_FTI = 0
        self.LastHang_AverageLoad = 0
        self.LastHang_MaximalLoad = 0
        self.LastHang_RFD = 0
        self.LastHang_LoadLoss = 0

        # Connect to MQTT
        self._client = mqtt.Client()
        self._client.connect(hostname, port,60)
        self._sendmessage("/status", "Starting")

        self.init_hx711()
        self._sendmessage("/status", "Calibration")

        self.calibrate()

        if EMULATE_HX711:
            simfile = "simulation_data.json"
            self._simcounter = 0
            with open(simfile) as json_file:
                data = json.load(json_file)
            self._simdata = data["SimulationData"]
            #print (self._simdata["time"])

        self._moving_average_n = 5
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
        self.hx = HX711(self.pin_dout , self.pin_pd_sck) 

        # I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
        # Still need to figure out why does it change.
        # If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
        # There is some code below to debug and log the order of the bits and the bytes.
        # The first parameter is the order in which the bytes are used to build the "long" value.
        # The second paramter is the order of the bits inside each byte.
        # According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
        self.hx.set_reading_format("MSB", "MSB")

        self.set_reference_unit()

        self.hx.reset()

    def calibrate(self):
        logging.debug("Starting Tare done! Wait...")
        self._sendmessage("/status", "Starting Tare done! Wait...")

        self.hx.tare()
        logging.debug("Tare done! Add weight now...")
        self._sendmessage("/status", "Tare done! Add weight now...")

        # to use both channels, you'll need to tare them both
        #hx.tare_A()
        #hx.tare_B()

    # TODO implement calibrate command over MQTT  #78

    def set_reference_unit(self):
        """
        HOW TO CALCULATE THE REFFERENCE UNIT
        To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
        In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
        and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
        If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
        hx.set_reference_unit(113)
        """
        #unit = 92
        #unit = 1257528 /79

        self.hx.set_reference_unit(self.referenceUnit)

    def run_main_measure(self):
        while True:
            try:
                # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
                # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
                # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
                
                # np_arr8_string = hx.get_np_arr8_string()
                # binary_string = hx.get_binary_string()
                # print binary_string + " " + np_arr8_string
                
                # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
                #val = self.hx.get_weight(1)
                #val = self.hx.read_long()
                #cur_timestamp = time.time()
                #print(cur_timestamp, val)
                self.run_one_measure()
                logging.debug ("Current time " + "{:.2f}".format(self.time_current)  + " load " + "{:.2f}".format(self.load_current) + " average load " + "{:.2f}".format(self.AverageLoad) + " calculated FTI " + "{:.2f}".format(self.FTI)
                + " maximal load " + "{:.2f}".format(self.MaximalLoad) + " RFD " + "{:.2f}".format(self.RFD) + " LoadLoss " + "{:.2f}".format(self.LoadLoss))

                # To get weight from both channels (if you have load cells hooked up 
                # to both channel A and B), do something like this
                #val_A = hx.get_weight_A(5)
                #val_B = hx.get_weight_B(5)
                #print "A: %s  B: %s" % ( val_A, val_B )

                #self.hx.power_down()
                #self.hx.power_up()
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
        self.time_current = time.time()

        self._load_current_raw = -1*self.hx.get_weight(1) # Never use this, but use a Low pass filter to get rid of the noise
        self.load_current = self._calc_moving_average() # FIXME

        if EMULATE_HX711:
            self._simcounter = self._simcounter+1
            if (self._simcounter+1 >= 100): #len(self._simdata["time"])): # FIXME does not work yet
                self._simcounter=0
            self.load_current = self._simdata["load"][self._simcounter]
            #time.sleep(0.05) # FIXME
            #logging.debug("Simulation: " + str(self._simcounter) + " load: " + str(self.load_current))

        self._detect_hang()
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


        logging.debug("Sensor current max load " + str(self.MaximalLoad) + " and last maximum " + str(self.LastHang_MaximalLoad))
        #self._sendmessage("/loadstatus", '{"time": ' + "{:.2f}".format(self.time_current) + ', "loadcurrent": '+ "{:.2f}".format(self.load_current) + ', "loadaverage": ' + "{:.2f}".format(self.AverageLoad) + ', "fti": ' + "{:.2f}".format(self.FTI) + ', "rfd": ' + "{:.2f}".format(self.RFD) + ', "loadmaximal": ' + "{:.2f}".format(self.MaximalLoad) + ', "loadloss": ' + "{:.2f}".format(self.LoadLoss) + '}')
        #(full_second, full_second_decimals) = divmod(self.time_current,1)
        #print (self.time_current)
        ##print (full_second)
        #print (full_second_decimals)
        #if full_second_decimals <= 0.02:
        self._sendmessage("/loadstatus", '{"time": ' + "{:.2f}".format(self.time_current) + ', "loadcurrent": '+ "{:.2f}".format(self.load_current) + ', "loadaverage": ' + "{:.2f}".format(self.AverageLoad) + ', "fti": ' + "{:.2f}".format(self.FTI) + ', "rfd": ' + "{:.2f}".format(self.RFD) + ', "loadmaximal": ' + "{:.2f}".format(self.MaximalLoad) + ', "loadloss": ' + "{:.2f}".format(self.LoadLoss) + '}')

    def _calc_avg_load(self):
        avg_load = sum(self._load_series) / len (self._load_series)
        self.AverageLoad = avg_load
        return avg_load

    def _fill_series(self):
        # Cut series down to _series_max_elements
        if (len(self._load_series) > self._series_max_elements):
            self._load_series.pop()
            self._time_series.pop()

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
        self.HangDetected = False
        if (self.load_current > self.load_hang):
            self.HangDetected = True

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
        FTI calculate the integraf force-time from a serie of StrengthData values
        Return value is expressed in Newton*second (-> Impulse)

        return integrate.Simpsons(x, fx)      func Simpsons(x, f []float64) float64

        f[i] = f(x[i]), x[0] = a, x[len(x)-1] = b

        \int_a^b f(x)dx

        """
        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.simpson.html
        #integrate.simpson(y, x)
        self.FTI = integrate.simpson(self._load_series, self._time_series) * self._Gravity
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
    a = SensorForce(sampling_interval = 0.005)
    a.calibrate()
    a.run_main_measure()
