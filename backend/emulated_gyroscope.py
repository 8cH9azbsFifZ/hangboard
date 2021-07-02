"""
Class for handling all stuff to simulate a gyroscope
"""


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Gyroscope(%(threadName)-10s) %(message)s',
                    )

import random


class Gyroscope():
    def __init__(self, verbose=None):
        logging.debug('Init Emulated Gyroscope Class')

    def run_one_measure (self):
        mini = -100
        maxi = 100
        self.gyroXAngle = float(random.randint(mini,maxi))
        self.compAngleX = float(random.randint(mini,maxi))
        self.kalAngleX = float(random.randint(mini,maxi))
        self.pitch = float(random.randint(mini,maxi))
        self.roll = float(random.randint(mini,maxi))
        self.gyroYAngle = float(random.randint(mini,maxi))
        self.compAngleY = float(random.randint(mini,maxi))
        self.kalAngleY = float(random.randint(mini,maxi))
        #logging.debug(str(self.roll)+"  "+str(self.gyroXAngle)+"  "+str(self.compAngleX)+"  "+str(self.kalAngleX)+"  "+str(self.pitch)+"  "+str(self.gyroYAngle)+"  "+str(self.compAngleY)+"  "+str(self.kalAngleY))

    def run_measure(self):
        while True:
            self.run_one_measure()

if __name__ == "__main__":
    a = Gyroscope()
    a.run_one_measure()
