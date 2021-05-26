import zmq

import time
import json
import argparse

from threading import Thread

parser = argparse.ArgumentParser(description="Exercise Timer Backend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
parser.add_argument ('--portrecv')
args = parser.parse_args()

HOST = args.host 
PORT = args.port 
PORTRECV = args.portrecv

class Exercise(Thread):
    def __init__(self):
        self.init_exercise()
        self.init_sender()
        self.init_receiver()

        Thread.__init__(self)
        self.active = True
        self.daemon = True

        self.start()

    def init_sender(self):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind('tcp://'+HOST+':'+PORT) #.format(HOST, PORT))
        self.zmq_count = 0

    def init_receiver(self):
        self._context_recv = zmq.Context()
        self._socket_recv = self._context_recv.socket(zmq.REP)
        self._socket_recv.bind('tcp://{}:{}'.format(HOST, PORTRECV)) 

    def init_exercise(self):
        self.filename = "./test.json" # TODO: as parameter
        with open(self.filename) as json_file:
            self.data = json.load(json_file)

        self.session = (self.data["Sessions"][0])
        self.session_name = self.session["Name"]
        self.total_exercises = len (self.session["Exercise"])
        self.current_exercise = 0
        self.current_exercise_name = "Rest to start"

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            print('Doing something imporant in the background')

            message = self._socket_recv.recv()
            self._socket_recv.send(b"Ok")

            print("Received request: %s" % message)
            if (message == b"Start"):
                self.run_exercise()
            #  Do some 'work'
            time.sleep(1)

            #  Send reply back to client

            #time.sleep(1)

    def run_exercise (self): 
        print ("Run one exercise")
        e = self.session["Exercise"][self.current_exercise]
        name = e["Type"]
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
                        self._socket.send_json(json.dumps({"Type": name, "Duration": duration, "Counter": counter, "Completed": completed, "Left": left, "Right": right}))

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
                    self._socket.send_json(json.dumps({"Type": "Pause", "Duration": pause_duration, "Counter": counter, "Completed": completed, "Left": left, "Right": right}))


if __name__ == "__main__":
    ex = Exercise()
    #ex.run_exercise()
    while True:
        print ("Main Task waiting")
        time.sleep(1)
