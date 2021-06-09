""" 
Classes containing all the timers
"""
import json
import os
import time

"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Timers(%(threadName)-10s) %(message)s',
                    )


import threading
"""
Use threading for threads
"""
from tabulate import tabulate 
""" 
Use tabulate for an ASCII Hanboard display for debugging purposes
"""

from pydispatch import dispatcher
"""
Use pydispatch and signals to transfer JSON data between the threads.
"""
from aio_pydispatch import Signal
SIGNAL_AIO_MESSAGER = Signal('SignalMessager')

SIGNAL_EXERCISETIMER = 'SignalExerciseTimer'
SIGNAL_PAUSETIMER = 'SignalPauseTimer'
SIGNAL_ASCIIBOARD = 'AsciiBoard'
SIGNAL_MESSAGER = 'SignalMessager'


class ExerciseTimer(threading.Thread):
    """
    All stuff for running an exercise timer.
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, dt=0.1):
        super(ExerciseTimer,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_EXERCISETIMER, sender=dispatcher.Any )

        # Time increment for counter in an exercise
        self.exercise_dt = dt
        self.exercise_t0 = 0
        self.exercise_t1 = 10
        self.exercise_t = 0
        self.exercise_rest = 10
        self.exercise_completed = 0

        self.timer_shall_run = False


        write_path = "/tmp/pipe.in"
        self.wf = os.open(write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)


    def pipe(self, message):
        
        #read_path = "/tmp/pipe.out"
        
        #rf = None
        
        #for i in range(1, 11):
        msg = message.encode() #"msg " + str(i)
        len_send = os.write(self.wf, msg)
        #print ("sent msg: %s" % msg)
        
            #if rf is None:
            #    rf = os.open(read_path, os.O_RDONLY)
        
            #s = os.read(rf, 1024)
            #if len(s) == 0:
            #    break
            #print "received msg: %s" % s
        
            #time.sleep(1)
        
        #os.write(wf, 'exit')
        
        #os.close(rf)
        #os.close(wf)



    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while True:
            if (self.do_stop == True):
                return
            time.sleep(1)
        return

    def assemble_message_timerstatus(self):
        msg = json.dumps({"Exercise": self.exercise, "Type": self.type, "Left": self.left, "Right": self.right, 
            "Counter": "{:.2f}".format(self.counter), "CurrentCounter": "{:.2f}".format(self.exercise_t), "Completed": "{:.0f}".format(self.exercise_completed), "Rest": "{:.2f}".format(self.exercise_rest)})
        logging.debug(msg)
        return (msg)

    def handle_signal (self, message):
        logging.debug('ExerciseTimer: Signal detected with ' + str(message) )

        logging.debug('Loading message')
        msg = json.loads(str(message))
        if ("Exercise" in msg):
            logging.debug('Loading exercise setup')

            self.exercise = msg["Exercise"]
            self.rest_to_start = msg["Rest-to-Start"]
            self.pause = msg["Pause"]
            self.reps = msg["Reps"]
            self.type = msg["Type"]
            self.left = msg["Left"]
            self.right = msg["Right"]
            self.counter = msg["Counter"]

            self.run_exercise()
            
        if ("StartExerciseTimer" in msg):
            logging.debug('Starting exercise timer due to hang')
            self.timer_shall_run = True

        if ("StopExerciseTimer" in msg):
            logging.debug('Stopping exercise timer due to no hang')
            self.timer_shall_run = False




    def run_exercise(self): 
        logging.debug('Run exercise')

        self.exercise_t0 = 0
        self.exercise_t1 = self.counter
        self.exercise_t = 0
        self.exercise_rest = self.counter
        self.exercise_completed = 0

        dispatcher.send( signal=SIGNAL_ASCIIBOARD, message="Hang")
        dispatcher.send( signal=SIGNAL_MESSAGER, message="Hang")
        self.pipe ("Hang")
        #SIGNAL_AIO_MESSAGER.send("Hang")

        while not self.timer_shall_run:
            time.sleep (self.exercise_dt)

        while (float(self.exercise_t) < float(self.exercise_t1 - 0.0001)):
            time.sleep (self.exercise_dt)
            self.exercise_t = self.exercise_t + self.exercise_dt
            self.exercise_rest = self.exercise_t1 - self.exercise_t
            self.exercise_completed = float(self.exercise_t) / float(self.exercise_t1) *100
            self.assemble_message_timerstatus()
            if (self.do_stop == True):
                return
            if (self.timer_shall_run == False):
                break
                



class PauseTimer(threading.Thread):
    """
    All stuff for running a pause timer.
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, dt=0.1):
        super(PauseTimer,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_PAUSETIMER, sender=dispatcher.Any )

        # Time increment for counter in an exercise
        self.dt = dt
        self.t0 = 0
        self.t1 = 10
        self.t = 0
        self.rest = 10
        self.completed = 0

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while True:
            if (self.do_stop == True):
                return
            time.sleep(1)
        return

    def handle_signal (self, message):
        logging.debug('PauseTimer: Signal detected with ' + str(message) )

        logging.debug('Get current pause time')
        self.t1 = float(message)
        self.run_pause()

    def run_pause(self): 
        logging.debug('Run pause')

        self.t0 = 0
        self.t = 0
        self.rest = self.t1
        self.completed = 0

        dispatcher.send( signal=SIGNAL_ASCIIBOARD, message="Pause")

        while (float(self.t) < float(self.t1 - 0.0001)):
            time.sleep (self.dt)
            self.t = self.t + self.dt
            self.rest = self.t1 - self.t
            self.completed = float(self.t) / float(self.t1) *100
            self.assemble_message_timerstatus()
            if (self.do_stop == True):
                return

    def assemble_message_timerstatus(self):
        msg = json.dumps({"Exercise": "Pause", "Type": "Pause", "Left": "", "Right": "", 
            "Counter": "{:.2f}".format(self.t1), "CurrentCounter": "{:.2f}".format(self.t), "Completed": "{:.0f}".format(self.completed), "Rest": "{:.2f}".format(self.rest)})
        logging.debug(msg)
        return (msg)
