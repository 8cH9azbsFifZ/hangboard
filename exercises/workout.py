"""
This is the new thread based implementation of the classes.
Lessons learned: Microservices are fine, but nanoservices not :)
"""

import json
import os
import time

"""
Implement logging with debug level from start on now :)
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
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

"""
Signals for communication
"""
SIGNAL_WORKOUT = 'SignalWorkout'
SIGNAL_MESSAGER = 'SignalMessager'
SIGNAL_EXERCISETIMER = 'SignalExerciseTimer'
SIGNAL_PAUSETIMER = 'SignalPauseTimer'
SIGNAL_ASCIIBOARD = 'AsciiBoard'
SIGNAL_BOARD = 'Board'


class Workout():
    def __init__(self, workoutfile="./workouts/workout-test.json"):
        self.select_workout(workoutfile)
        self.exercise_status = "Status"
        self.workout_number = 0
        self.workout = (self.data["Workouts"][self.workout_number])
        self.workout_name = self.workout["Name"]
        self.total_sets = len (self.workout["Sets"])
        self.current_set = 0
        self.current_set_name = "Rest to start"

        # Variable to check if ready or somebody hanging
        self.exercise_hanging = False

        # Thread controlling
        self.do_stop = False

        # Signals handler setup
        dispatcher.connect( self.handle_signal_workout, signal=SIGNAL_WORKOUT, sender=dispatcher.Any )


    def select_workout(self, filename):
        self.workoutfile = filename # FIXME
        self.filename = self.workoutfile

        with open(self.filename) as json_file:
            self.data = json.load(json_file)

    def list_workouts(self):
        logging.debug("List workouts")
        self.workoutdir = "./workouts"
        workout_array = []
        
        for filename in os.listdir (self.workoutdir):
            if filename.endswith ("json"):
                fn = os.path.join(self.workoutdir, filename)
                with open(fn) as json_file:
                    data = json.load(json_file)

                    for workout in (data["Workouts"]):
                        print (workout["Name"], fn)
                        workout_array.append({"Name": workout["Name"], "ID": workout["ID"]})
        print (workout_array)
        
        self.exercise_status = json.dumps({"WorkoutList": workout_array, "OneMessageOnly": True})

    def show_workout(self):
        print (self.data)

    def show_set(self):
        set = self.workout["Sets"][self.current_set]
        print (set)

    def show_exercise(self):
        exercise = self.workout["Sets"][self.current_set]["Exercise"]
        print (exercise)

    def run_workout (self):
        """
        Run a single workout
        """
        for w in range (0, self.total_sets+1):
            self.current_set = w
            self.run_set()

    def run_exercise_maximal_hang(self):
        logging.debug("Run a maximal hang time exercise")
        # TBD Implement

    def run_exercise_pull_ups(self):
        logging.debug("Run a pull ups exercise")
        # TBD Implement

    def __get_current_set(self):
        logging.debug('Get current set')

        self.exercise = self.workout["Sets"][self.current_set]["Exercise"]
        self.rest_to_start = self.workout["Sets"][self.current_set]["Rest-to-Start"]
        self.pause = self.workout["Sets"][self.current_set]["Pause"]
        self.reps = self.workout["Sets"][self.current_set]["Reps"]
        self.type = self.workout["Sets"][self.current_set]["Type"]
        self.left = self.workout["Sets"][self.current_set]["Left"]
        self.right = self.workout["Sets"][self.current_set]["Right"]
        self.counter = self.workout["Sets"][self.current_set]["Counter"]


    def run_pause(self):
        logging.debug('Run pause')

    def run_set(self):
        self.__get_current_set()
        logging.debug('Run exercise')
        self.rep_current = 0
        dispatcher.send( signal=SIGNAL_PAUSETIMER, message=self.rest_to_start)
        for self.rep_current in range (0, self.reps):
            self.__get_current_set()
            #print (self.rep_current)
            dispatcher.send( signal=SIGNAL_EXERCISETIMER, message=json.dumps(self.workout["Sets"][self.current_set]))
            dispatcher.send( signal=SIGNAL_PAUSETIMER, message=self.pause)

    def handle_signal_workout (self, message):
        logging.debug('Signal detected with ' + str(message) )
        #self.run_set()

    def run_test (self):
        logging.debug('Run test')

        self.__get_current_set()
        dispatcher.send( signal=SIGNAL_EXERCISETIMER, message=json.dumps(self.workout["Sets"][self.current_set]))

class PauseTimer(threading.Thread):
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

class ExerciseTimer(threading.Thread):
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

        logging.debug('Get current set')
        msg = json.loads(str(message))

        self.exercise = msg["Exercise"]
        self.rest_to_start = msg["Rest-to-Start"]
        self.pause = msg["Pause"]
        self.reps = msg["Reps"]
        self.type = msg["Type"]
        self.left = msg["Left"]
        self.right = msg["Right"]
        self.counter = msg["Counter"]

        self.run_exercise()

    def run_exercise(self): 
        logging.debug('Run exercise')

        self.exercise_t0 = 0
        self.exercise_t1 = self.counter
        self.exercise_t = 0
        self.exercise_rest = self.counter
        self.exercise_completed = 0

        dispatcher.send( signal=SIGNAL_ASCIIBOARD, message="Hang")

        while (float(self.exercise_t) < float(self.exercise_t1 - 0.0001)):
            time.sleep (self.exercise_dt)
            self.exercise_t = self.exercise_t + self.exercise_dt
            self.exercise_rest = self.exercise_t1 - self.exercise_t
            self.exercise_completed = float(self.exercise_t) / float(self.exercise_t1) *100
            self.assemble_message_timerstatus()
            if (self.do_stop == True):
                return

                
class Messager(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(Messager,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_MESSAGER, sender=dispatcher.Any )

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
        logging.debug('Messager: Signal detected with ' + str(message) )

class Board(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, boardname = "zlagboard_evo"):
        super(Board,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_BOARD, sender=dispatcher.Any )

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
        logging.debug('Board: Signal detected with ' + str(message) )

class AsciiBoard(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(AsciiBoard,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_ASCIIBOARD, sender=dispatcher.Any )

        self.set_board_default()
        self.render_board()

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
        logging.debug('Asciiboard: Signal detected with ' + str(message) )
        if (message == "Hang"):
            self.set_active_holds()
        else:
            self.set_board_default()
        self.render_board()

    def set_board_default(self):
        self.board_row1 = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]
        self.board_row2 = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]
        self.board_row3 = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]

    def set_active_holds(self):
        hold1 = "A1"
        hold2 = "A7"
        for index, item in enumerate(self.board_row1):
            if ((item == hold1) or (item == hold2)):
                self.board_row1[index] = "**"
            
    def render_board(self):
        self.board = (tabulate([self.board_row1, self.board_row2, self.board_row3], tablefmt="grid"))
        print (self.board)


if __name__ == "__main__":
    mm = Messager()
    mm.start()
    ex = ExerciseTimer(dt=1)
    ex.start()
    pa = PauseTimer(dt=1)
    pa.start()
    bb = Board()
    bb.start()
    ab = AsciiBoard()
    ab.start()
    wa = Workout()
    wa.run_set()
