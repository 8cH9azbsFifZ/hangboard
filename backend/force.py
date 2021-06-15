"""
Force Measurement Backend
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='SensorForce(%(threadName)-10s) %(message)s',
                    )

import time
import sys

import json

import threading

# TODO: Run in background at all times or send signals?

EMULATE_HX711 = False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
    GPIO.setmode(GPIO.BCM) # Set PIN names to "GPIO**", such that these number correspond to the images.
    # https://raspi.tv/2013/rpi-gpio-basics-4-setting-up-rpi-gpio-numbering-systems-and-inputs

else:
    from emulated_hx711 import HX711


class SensorForce():
    def __init__(self, EMULATE_HX711 = True, pin_dout = 17, pin_pd_sck = 27, sampling_rate = 0.1, referenceUnit = 1257528/79, load_hang = 1257528/79*0.2 ):
        logging.debug ("Initialize")

        self.pin_dout = pin_dout
        self.pin_pd_sck = pin_pd_sck

        self.referenceUnit = referenceUnit
        self.sampling_rate = sampling_rate

        self.calibration_duration = 10

        self.HangDetected = False
        self.HangStateChanged = False

        self.load_hang = load_hang
        self.load_current = 0

        self.LastHangTime = 0
        self.LastPauseTime = 0
        self.TimeStateChangeCurrent = time.time()       
        self.TimeStateChangePrevious = self.TimeStateChangeCurrent

        self.init_hx711()



    def cleanAndExit(self):
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
        self.hx.tare()

        logging.debug("Tare done! Add weight now...")

        # to use both channels, you'll need to tare them both
        #hx.tare_A()
        #hx.tare_B()

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
                val = self.hx.get_weight(1)
                #val = self.hx.read_long()
                cur_timestamp = time.time()
                print(cur_timestamp, val)

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

    def run_one_measure(self):
        self.load_current = self.hx.get_weight(1)

        self.detect_hang()

        self.hx.power_down() #FIXME
        self.hx.power_up()
        time.sleep(self.sampling_rate)

    def NobodyHanging(self):
        pass
        # TODO: implement

    def Changed(self):
        pass
        # TODO: implement

    def detect_hang(self):
        oldstate = self.HangDetected

        if (self.load_current > self.load_hang):
            self.HangDetected = True
        else:
            self.HangDetected = False
            

        if (oldstate == self.HangDetected):
            self.HangStateChanged = False
        else:
            self.HangStateChanged = True

            self.TimeStateChangePrevious = self.TimeStateChangeCurrent
            self.TimeStateChangeCurrent = time.time()

            if (self.HangDetected == True):
                self.LastHangTime = self.TimeStateChangeCurrent - self.TimeStateChangePrevious
            else:
                self.LastPauseTime = self.TimeStateChangeCurrent - self.TimeStateChangePrevious

        #logging.debug ("Hang detected: " + str(self.HangDetected) + " with angle " + str(angle) + "in " + str(self.AngleX_Hang) + " and " + str(self.AngleX_NoHang))

        return self.HangDetected

if __name__ == "__main__":
    #a = SensorForce(referenceUnit = 1)
    a = SensorForce(sampling_rate = 0.005)
    a.calibrate()
    a.run_main_measure()
