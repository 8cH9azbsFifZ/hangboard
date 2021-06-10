"""
Class for handling all stuff to create a zlagboard sensor.
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='SensorZlagboard(%(threadName)-10s) %(message)s',
                    )

import time
import json


EMULATE_GYROSCOPE = False

if not EMULATE_GYROSCOPE:
    from gyroscope import Gyroscope
else:
    from emulated_gyroscope import Gyroscope

SIGNAL_ZLAGBOARD = "SignalZlagboard"
SIGNAL_WORKOUT = 'SignalWorkout'

class SensorZlagboard(Gyroscope):
    def __init__(self, verbose=None, dt=0.1, AngleX_Hang=-43., AngleX_NoHang=43.):
        super(SensorZlagboard, self).__init__()

        self.calibration_duration = 10

        self.HangDetected = False
        self.HangStateChanged = False
        self.AngleX_Hang = AngleX_Hang
        self.AngleX_NoHang = AngleX_NoHang

        self.LastHangTime = 0
        self.LastPauseTime = 0
        self.TimeStateChangeCurrent = time.time()       
        self.TimeStateChangePrevious = self.TimeStateChangeCurrent

        self.sampling_interval = 0.1

    def run_one_measure(self):
        self.run_one_measure_gyroscope()
        self.detect_hang()

    def NobodyHanging(self):
        self.run_one_measure()
        return not self.HangDetected

    def Changed(self):
        self.run_one_measure()

        if (self.HangStateChanged == True):
            if (self.HangDetected == True):
                logging.debug ("HangStateChanged and HangDetected")
                return "Hang"
            else:
                logging.debug ("HangStateChanged and no HangDetected")
                return "NoHang"
        else:
            return ""

    def run_one_measure_gyroscope(self):
        super(SensorZlagboard, self).run_one_measure()

    def detect_hang(self):
        """
        Detect a hang based on the calibrated hang / no hang angles.
        A state change variable will also be set.
        """
        logging.debug ("Detect hang")

        angle = self.kalAngleX

        oldstate = self.HangDetected
        self.HangDetected = False

        if (self.AngleX_Hang > self.AngleX_NoHang):
            delta = self.AngleX_Hang - self.AngleX_NoHang
            logging.debug (str(delta) + " " + str(angle+delta))
            if (angle + delta > self.AngleX_Hang):
                self.HangDetected = True
        else:
            delta = self.AngleX_NoHang - self.AngleX_Hang
            logging.debug (str(delta) + " " + str(angle-delta))
            if (angle - delta < self.AngleX_Hang):
                self.HangDetected = True

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

        logging.debug ("Hang detected: " + str(self.HangDetected) + " with angle " + str(angle) + "in " + str(self.AngleX_Hang) + " and " + str(self.AngleX_NoHang))

        return self.HangDetected

    def assemble_message(self):
        """
        Assemble the status message.
        """
        self.message = json.dumps(
            {"AngleX": "{:.2f}".format(self.kalAngleX), "AngleY": "{:.2f}".format(self.kalAngleY),
            "AngleX_NoHang": "{:.2f}".format(self.AngleX_NoHang), "AngleX_Hang": "{:.2f}".format(self.AngleX_Hang),
            "HangDetected": self.HangDetected, "HangStateChanged": self.HangStateChanged,
            "LastHangTime": "{:.2f}".format(self.LastHangTime), "LastPauseTime": "{:.2f}".format(self.LastPauseTime)
        })
        return (self.message)

    def calibrate (self):
        """
        Routine for measure the extrema -> measure two times ten seconds one shot
        """
        
        dt = 0.1
        tt = 0.0
        print ("No hang")	
        while (tt < self.calibration_duration):
            tt = tt + dt
            self.run_one_measure_gyroscope()
            time.sleep(dt)
        self.AngleX_NoHang = self.kalAngleX

        print ("Time to hang")
        tt = 0.0	
        while (tt < self.calibration_duration):
            tt = tt + dt
            time.sleep(dt)
            self.run_one_measure_gyroscope()
        self.AngleX_Hang = self.kalAngleX # FIXME: sum of both angles - direction indenpendent?!

        print ('Calibration done with no hang angle ' + str(self.AngleX_NoHang) + " and hang angle " + str(self.AngleX_Hang))
        logging.debug('Calibration done with no hang angle ' + str(self.AngleX_NoHang) + " and hang angle " + str(self.AngleX_Hang))


if __name__ == "__main__":
    a = SensorZlagboard()
    #a.calibrate()
    while True:
        print (a.Changed())
        time.sleep(1)

