from flask import Flask, render_template, request, Response, redirect, url_for, session
import zmq

import time
import json
import os

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
PORTRECV = os.getenv("PORTRECV")
TASK_SOCKET = zmq.Context().socket(zmq.SUB)
TASK_SOCKET.connect('tcp://{}:{}'.format(HOST, PORT))
TASK_SOCKET.subscribe("")


context = zmq.Context()

#  Socket to talk to server 
socket = context.socket(zmq.REQ) # FIXME
socket.connect("tcp://"+HOST+":"+PORTRECV+"")


app = Flask(__name__) 
app.secret_key = "test"

@app.route("/", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Start') == 'Start':
            # pass
            print("Start Exercise")
            socket.send(b"Start")
            message = socket.recv()
            print (message)
            return render_template("index.html")
        elif  request.form.get('Stop') == 'Stop':
            # pass # do something else
            print("Stop Exercise")
            socket.send(b"Stop")
            message = socket.recv()
            print (message)
            return render_template("index.html")
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

        while 1:
            results = TASK_SOCKET.recv_json()
            print (results)
            data = json.loads(results)
            yield "data:" + results + "\n\n"

            time.sleep(.11)
    return Response(generate(), mimetype= 'text/event-stream')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
