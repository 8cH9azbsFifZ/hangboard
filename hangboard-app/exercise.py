import zmq

import time
import json

HOST = '127.0.0.1'
PORT = 9090

class Exercise():
    def __init__(self):
        self.filename = "../exercises/test.json" # TODO: as parameter
        with open(self.filename) as json_file:
            self.data = json.load(json_file)

        self.session = (self.data["Sessions"][0])
        self.session_name = self.session["Name"]
        self.total_exercises = len (self.session["Exercise"])
        self.current_exercise = 0
        self.current_exercise_name = "Rest to start"

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind('tcp://{}:{}'.format(HOST, PORT))

        self.zmq_count = 0


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
                    for counter in range (0, duration+1):
                        time.sleep (1)
                        completed = counter / duration *100
                        self._socket.send_json(json.dumps({"Type": name, "Duration": duration, "Counter": counter, "Completed": completed}))

                elif (name == "Maximal Hang"):
                    print ("Key press?")                    
                elif (name == "Assisted Pull Ups"):
                    print ("Key press?")                    
                else:
                    print ("Key press?")

                print ("Pause")
                for counter in range (0, pause_duration+1):
                    time.sleep (1)
                    completed = counter / pause_duration *100
                    self._socket.send_json(json.dumps({"Type": "Pause", "Duration": pause_duration, "Counter": counter, "Completed": completed}))


if __name__ == "__main__":
    ex = Exercise()
    ex.run_exercise()
