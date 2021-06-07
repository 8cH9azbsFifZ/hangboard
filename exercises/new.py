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

class ExerciseTimer():
    def __init__(self, name="t1", delay=2):
        logging.debug('Init class')
        self.__timer = self.__start_timer(name, delay)

    def delayed(self):
        logging.debug('worker running')
        t = threading.currentThread()
        while not getattr(t, "do_stop", False):
            logging.debug('Looping')
            time.sleep(1)
        return

    def __start_timer(self, name, delay):
        tname = threading.Timer(delay, self.delayed)
        tname.setName(name)
        logging.debug('starting timers')
        tname.start()
        return tname

    def stop_timer(self):
        self.__timer.do_stop = True    
    


class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(ConsumerThread,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        #return

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while True:
            if (self.do_stop == True):
                return
            if not q.empty():
                item = q.get()
                logging.debug('Getting ' + str(item) + ' : ' + str(q.qsize()) + ' items in queue')
                time.sleep(random.random())
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
    et = ExerciseTimer(name="t1", delay=2)
    es = ExerciseTimer(name="t2", delay=3)
    p = Produce(name='producer')
    p.start()


    time.sleep(1)
    et.stop_timer()
    time.sleep(2)
    qq = ConsumerThread(name='consumer')
    qq.start()
    es.stop_timer()
    time.sleep(5)
    p.stop()
    qq.stop()
    logging.debug('done')