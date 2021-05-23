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

@app.route("/svg", methods=['GET', 'POST'])
def svg():
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
    return render_template("svg.html")


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




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
