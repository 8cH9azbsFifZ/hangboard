from flask import Flask, render_template, request, Response, redirect, url_for, session
import zmq

import time
import json

HOST = '127.0.0.1'
PORT = 9090
TASK_SOCKET = zmq.Context().socket(zmq.SUB)
TASK_SOCKET.connect('tcp://{}:{}'.format(HOST, PORT))
TASK_SOCKET.subscribe("")

app = Flask(__name__) 
app.secret_key = "test"

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
    return render_template("index.html")

@app.route('/progress')
def progress():
    def generate():
        #x = 0
        #
        #while x <= 100:
        #    yield "data:" + str(x) + "\n\n"
        #    x = x + 10
        #    time.sleep(.11)
        while 1:
            results = TASK_SOCKET.recv_json()
            #x = results["Completed"]
            print (results)
            data = json.loads(results)
            #completed = data["Completed"]
            print (data["Completed"])
            x=data["Completed"]
            yield "data:" + str(x) + "\n\n"
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
    #TASK_SOCKET.send_json({"command": "pause"})
    results = TASK_SOCKET.recv_json()
    return f"pausing {results}"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
