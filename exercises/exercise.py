import zmq

import time
import json
import argparse

from threading import Thread

parser = argparse.ArgumentParser(description="Workout Timer Backend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
parser.add_argument ('--portrecv')
args = parser.parse_args()

HOST = args.host 
PORT = args.port 
PORTRECV = args.portrecv

workoutfile = "workout-test.json"

class Workout(Thread):
    def __init__(self):
        self.init_workout()
        self.init_sender()
        self.init_receiver()

        Thread.__init__(self)
        self.active = True
        self.daemon = True

        self.start()

    def init_sender(self):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind('tcp://{}:{}'.format(HOST, PORT)) 
        self.zmq_count = 0

    def init_receiver(self):
        self._context_recv = zmq.Context()
        self._socket_recv = self._context_recv.socket(zmq.REP)
        self._socket_recv.bind('tcp://{}:{}'.format(HOST, PORTRECV)) 

    def init_workout(self):
        self.filename = workoutfile

        with open(self.filename) as json_file:
            self.data = json.load(json_file)

        self.workout_number = 0
        self.workout = (self.data["Workouts"][self.workout_number])
        self.workout_name = self.workout["Name"]
        self.total_sets = len (self.workout["Sets"])
        self.current_set = 0
        self.current_set_name = "Rest to start"

    def run(self):
        """ Method that runs forever """
        while True:
            message = self._socket_recv.recv()
            self._socket_recv.send(b"Ok") # FIXME

            print("Received request: %s" % message)
            if (message == b"Start"):
                self.run_set()

            time.sleep(1)

    def run_workout (self):
        for w in range (0, self.total_sets+1):
            self.current_set = w
            self.run_set()


    def run_set (self): 
        print ("Run one set")
        e = self.workout["Sets"][self.current_set]
        name = e["Exercise"]
        reps_total = e["Reps"]
        duration = e["Counter"]
        pause_duration = e["Pause"]
        rest_to_start = e["Rest-to-Start"]

        for reps_counter in range (1, 1+reps_total):
            start_detected = 1
            if (start_detected == 1):
                if (name == "Hang"):
                    print ("Hang")
                    left = "A1" # TODO: select 1st jug in list
                    right = "A7"  # TODO: select last jug in list
                    for counter in range (0, duration+1):
                        time.sleep (1)
                        completed = int(counter / duration *100)
                        self._socket.send_json(json.dumps({"Exercise": name, "Duration": duration, "Counter": counter, "Completed": completed, "Left": left, "Right": right}))

                elif (name == "Maximal Hang"):
                    print ("Key press?")                    
                elif (name == "Assisted Pull Ups"):
                    print ("Key press?")                    
                else:
                    print ("Key press?")

                print ("Pause")
                left = ""
                right = ""
                for counter in range (0, pause_duration+1):
                    time.sleep (1)
                    completed = int(counter / pause_duration *100)
                    self._socket.send_json(json.dumps({"Exercise": "Pause", "Duration": pause_duration, "Counter": counter, "Completed": completed, "Left": left, "Right": right}))


if __name__ == "__main__":
    ex = Workout()
    while True:
        print ("Exercise Timer Backend running")
        time.sleep(1)
