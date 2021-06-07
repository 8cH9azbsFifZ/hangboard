import threading
import time
import random

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

import Queue
BUF_SIZE = 100
q = Queue.Queue(BUF_SIZE)

class ExerciseTimer(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, t0 = 0, t1 = 10, dt=1):
        super(ExerciseTimer,self).__init__()
        self.target = target
        self.name = name
        self.dt = dt
        self.t0 = t0
        self.t1 = t1
        self.t = t0
        self.rest = t1
        self.do_stop = False

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while (self.t < self.t1):
            self.t = self.t + self.dt
            self.rest = self.t1 - self.t
            if (self.do_stop == True):
                return
            print (self.t)
            print (self.rest)
        return


class Produce(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        logging.debug('Init class and start thread ' + name)
        super(Produce,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while True:
            if (self.do_stop == True):  
                return
            if not q.full():
                item = random.randint(1,10)
                q.put(item)
                logging.debug('Putting ' + str(item) + ' : ' + str(q.qsize()) + ' items in queue')
                time.sleep(random.random())
        return





if __name__ == "__main__":
    et = ExerciseTimer(name="Test")
    et.start()
