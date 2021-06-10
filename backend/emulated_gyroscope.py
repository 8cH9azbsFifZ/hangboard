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
        self.gyroXAngle = float(random.randint(-10,10))
        self.compAngleX = float(random.randint(-10,10))
        self.kalAngleX = float(random.randint(-10,10))
        self.pitch = float(random.randint(-10,10))
        self.roll = float(random.randint(-10,10))
        self.gyroYAngle = float(random.randint(-10,10))
        self.compAngleY = float(random.randint(-10,10))
        self.kalAngleY = float(random.randint(-10,10))
        logging.debug(str(self.roll)+"  "+str(self.gyroXAngle)+"  "+str(self.compAngleX)+"  "+str(self.kalAngleX)+"  "+str(self.pitch)+"  "+str(self.gyroYAngle)+"  "+str(self.compAngleY)+"  "+str(self.kalAngleY))

    def run_measure(self):
        while True:
            self.run_one_measure()

if __name__ == "__main__":
    a = Gyroscope()
    a.run_measure()
