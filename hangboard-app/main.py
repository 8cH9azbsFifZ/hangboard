from flask import Flask, render_template, request, Response, redirect, url_for, session
import zmq
from threading import Thread

import time
import json
#from hx711 import HX711

HOST = '127.0.0.1'
PORT = 9090
TASK_SOCKET = zmq.Context().socket(zmq.REQ)
TASK_SOCKET.connect('tcp://{}:{}'.format(HOST, PORT))
app = Flask(__name__) 
app.secret_key = "test"


#try:
#    hx711 = HX711(
#    dout_pin=5,
#    pd_sck_pin=6,
#    channel='A',
#    gain=64
#    )
#
#    hx711.reset()   # Before we start, reset the HX711 (not obligate)
#    measures = hx711.get_raw_data(num_measures=3)
#finally:
#    GPIO.cleanup()  # always do a GPIO cleanup in your scripts!
#
#print("\n".join(measures))


class Exercise:
    def __init__ (self):
        self.filename = "../exercises/test.json" # TODO: as parameter
        with open(self.filename) as json_file:
            self.data = json.load(json_file)
            self.session = (self.data["Sessions"][0])
            self.session_name = self.session["Name"]
            self.total_exercises = len (self.session["Exercise"])
            self.current_exercise = 0
            self.current_exercise_name = "Rest to start"
    
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
                if (e["Type"] == "Hang"):
                    print ("Hang")
                    for self.current_exercise_counter in range (0, self.current_exercise_duration+1):
                        time.sleep (1)
                elif (e["Type"] == "Maximal Hang"):
                    print ("Key press?")                    
                elif (e["Type"] == "Assisted Pull Ups"):
                    print ("Key press?")                    
                else:
                    print ("Key press?")

                print ("Pause")
                for self.current_exercise_counter in range (0, self.current_exercise_pause_duration+1):
                    time.sleep (1)

# Ref: https://gist.github.com/blakebjorn/aab2f989a7b68fa83410153181aabbac
class Worker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self.active = True

    def run(self):
        self._socket.bind('tcp://{}:{}'.format(HOST, PORT))
        self._socket.setsockopt(zmq.RCVTIMEO, 500)
        while self.active:
            ev = self._socket.poll(1000)
            if ev:
                rec = self._socket.recv_json()
                self._socket.send_json({"response": "ok", "payload": rec})


ex = Exercise()

@app.route("/", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Encrypt') == 'Encrypt':
            # pass
            print("Encrypted")
            ex.run_exercise()
        elif  request.form.get('Decrypt') == 'Decrypt':
            # pass # do something else
            print("Decrypted")
        else:
            # pass # unknown
            return render_template("index.html")
    elif request.method == 'GET':
        # return render_template("index.html")
        print("No Post Back Call")
    return render_template("index.html", Exercise_Name = ex.current_exercise_name, Current_Exercise = ex.current_exercise, Total_Exercises = ex.total_exercises)

@app.route('/progress')
def progress():
    def generate():
        x = 0

        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(.11)

    
    return Response(generate(), mimetype= 'text/event-stream')

@app.route("/hang", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        #exercise = int(request.form["exercise"])
        #rest = int(request.form["rest"])
        #sets = int(request.form["sets"])
        ex.config_exercise()
        session["exercise"] = ex.current_exercise_duration
        session["rest"] = ex.current_exercise_pause_duration
        session["sets"] = ex.current_exercise_reps_total
        session["set_counter"] = 0

        return redirect(url_for("rest"))
    return render_template("hang_config.jinja2")


# Timer App
@app.route("/test", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        exercise = int(request.form["exercise"])
        rest = int(request.form["rest"])
        sets = int(request.form["sets"])

        session["exercise"] = exercise
        session["rest"] = rest
        session["sets"] = sets
        session["set_counter"] = 0

        return redirect(url_for("rest"))
    return render_template("home.jinja2")


@app.route("/rest")
def rest():
    return render_template("rest.jinja2", rest=session["rest"])


@app.route("/exercise")
def exercise():
    if session["set_counter"] == session["sets"]:
        return redirect(url_for("completed"))
    session["set_counter"] += 1
    return render_template("exercise.jinja2", exercise=session["exercise"])


@app.route("/complete")
def completed():
    return render_template("complete.jinja2", sets=session["set_counter"])


# Worker App test

@app.route("/start")
def start():
    TASK_SOCKET.send_json({"command": "start"})
    results = TASK_SOCKET.recv_json()
    return f"starting {results}"


@app.route("/pause")
def pause():
    TASK_SOCKET.send_json({"command": "pause"})
    results = TASK_SOCKET.recv_json()
    return f"pausing {results}"

if __name__ == "__main__":
    worker = Worker()
    worker.start() 
    app.run(host="127.0.0.1", port=8080, debug=True)
