"""
Class for handling all stuff to create a zlagboard sensor.
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='SensorZlagboard(%(threadName)-10s) %(message)s',
                    )

import time

from pydispatch import dispatcher
import json


EMULATE_GYROSCOPE = False

if not EMULATE_GYROSCOPE:
    from gyroscope import Gyroscope
else:
    from emulated_gyroscope import Gyroscope

SIGNAL_ZLAGBOARD = "SignalZlagboard"
SIGNAL_WORKOUT = 'SignalWorkout'

class SensorZlagboard(Gyroscope):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, dt=0.1):
        super(SensorZlagboard, self).__init__()

        self.calibration_duration = 1

        self.HangDetected = False
        self.HangStateChanged = False
        self.AngleX_Hang = 0
        self.AngleX_NoHang = 0

        self.LastHangTime = 0
        self.LastPauseTime = 0
        self.TimeStateChangeCurrent = time.time()       
        self.TimeStateChangePrevious = self.TimeStateChangeCurrent

        self.do_stop = False

        dispatcher.connect( self.handle_signal, signal=SIGNAL_ZLAGBOARD, sender=dispatcher.Any )

    def run(self):
        while True:
            self.run_one_measure()
            self.detect_hang()

            if (self.HangStateChanged == True):
                if (self.HangDetected == True):
                    logging.debug ("HangStateChanged and HangDetected")
                else:
                    logging.debug ("HangStateChanged and no HangDetected")

            if (self.do_stop == True):
                return
            time.sleep(1)
        return

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run_one_measure(self):
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
            if (angle + delta > self.AngleX_Hang):
                self.HangDetected = True
        else:
            delta = self.AngleX_NoHang - self.AngleX_Hang
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

        logging.debug ("Hang detected: " + str(self.HangDetected))

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
            self.run_one_measure()
            time.sleep(dt)
        self.AngleX_NoHang = self.kalAngleX

        print ("Time to hang")
        tt = 0.0	
        while (tt < self.calibration_duration):
            tt = tt + dt
            time.sleep(dt)
            self.run_one_measure()
        self.AngleX_Hang = self.kalAngleX # FIXME: sum of both angles - direction indenpendent?!

        logging.debug('Calibration done with no hang angle ' + str(self.AngleX_NoHang) + " and hang angle " + str(self.AngleX_Hang))

    def handle_signal (self, message):
        logging.debug('Signal detected with ' + str(message) )
        if (message == "Calibrate"):
            self.calibrate()

if __name__ == "__main__":
    a = SensorZlagboard()
    a.start()
    dispatcher.send( signal=SIGNAL_ZLAGBOARD, message="Calibrate")
    a.stop()

