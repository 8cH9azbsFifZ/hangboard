"""
Class containing all stuff for the distance sensor
"""

import RPi.GPIO as GPIO
import time
 
class SensorDistance():
    def __init__(self, pin_trigger=18, pin_echo=24):
        #GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)
 
        #set GPIO Pins 
        self._GPIO_TRIGGER = pin_trigger
        self._GPIO_ECHO = pin_echo

        #Set GPIO pin modes: in / out
        GPIO.setup(self._GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self._GPIO_ECHO, GPIO.IN)

        self._R = 40
        self._H = 1
        self._Q = 10
        self._P = 0
        self._U_hat = 0
        self._K = 0

    def kalman(self, U):
        self._K = self._P*self._H/(self._H*self._P*self._H+self._R)
        self._U_hat += + self._K*(U-self._H*self._U_hat)
        self._P = (1-self._K*self._H)*self._P+self._Q
        return self._U_hat

    def distance(self):
        # setze Trigger auf HIGH
        GPIO.output(self._GPIO_TRIGGER, True)
    
        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.00001)
        GPIO.output(self._GPIO_TRIGGER, False)
    
        tstart = time.time()
        tstop = time.time()
    
        # store start time
        while GPIO.input(self._GPIO_ECHO) == 0:
            tstart = time.time()
    
        # store stop time
        while GPIO.input(self._GPIO_ECHO) == 1:
            tstop = time.time()
    
        TimeElapsed = tstop - tstart
        # multiply by velocity of sound (34300 cm/s) 
        # and divide by two (forth and back)
        distance = (TimeElapsed * 34300) / 2
    
        return distance
 
    def Stop(self):
        GPIO.cleanup()


if __name__ == '__main__':
    d = SensorDistance()
    try:
        while True:
            distance = d.distance()
            if (distance < 5000):
                fabs = d.kalman (distance)
                print ("Distance = %.1f cm and %.1f cm with kalman" % (distance, fabs))
            time.sleep(.005)
 
    except KeyboardInterrupt:
        print("Done")
        d.Stop()
