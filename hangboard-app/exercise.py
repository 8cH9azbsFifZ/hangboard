import zmq

import time
import json

HOST = '127.0.0.1'
PORT = 9090
TASK_SOCKET = zmq.Context().socket(zmq.REQ)
TASK_SOCKET.connect('tcp://{}:{}'.format(HOST, PORT))

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


    def config_exercise (self):
        e = self.session["Exercise"][self.current_exercise]
        self.current_exercise_name = e["Type"]
        self.current_exercise_reps_counter = 0
        self.current_exercise_reps_total = e["Reps"]
        self.current_exercise_duration = e["Counter"]
        self.current_exercise_counter = 0
        self.current_exercise_pause_duration = e["Pause"]
        self.current_exercise_rest_to_start = e["Rest-to-Start"]

    def run_exercise (self): 
        print ("Run one exercise")
        self.config_exercise()

        for self.current_exercise_reps_counter in range (1, 1+self.current_exercise_reps_total):
            start_detected = 1
            if (start_detected == 1):
                print ("Start detected")
                if (self.current_exercise_name == "Hang"):
                    print ("Hang")
                    counter = 0
                    for self.current_exercise_counter in range (0, self.current_exercise_duration+1):
                        time.sleep (1)
                        self._socket.send_string("%d %d" % (1, counter))
                        #send_json
                        counter = counter + 1
                        print ("x")
                elif (self.current_exercise_name == "Maximal Hang"):
                    print ("Key press?")                    
                elif (self.current_exercise_name == "Assisted Pull Ups"):
                    print ("Key press?")                    
                else:
                    print ("Key press?")

                print ("Pause")
                for self.current_exercise_counter in range (0, self.current_exercise_pause_duration+1):
                    time.sleep (1)




if __name__ == "__main__":
    ex = Exercise()
    ex.run_exercise()
