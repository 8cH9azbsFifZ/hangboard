from flask import Flask, render_template, request, Response, session

import argparse
parser = argparse.ArgumentParser(description="Webinterface Frontend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
args = parser.parse_args()

app = Flask(__name__) 
app.secret_key = "test"

@app.route("/")
def index():
    print(request.method)
    return render_template("index.html")

@app.route("/calibration")
def calibration():
    print(request.method)
    return render_template("calibration.html")

@app.route("/selectexercise")
def selectexercise():
    print(request.method)
    return render_template("selectexercise.html")

@app.route("/config")
def config():
    print(request.method)
    return render_template("config.html")


if __name__ == "__main__":
    app.run(host=args.host, port=args.port, debug=True)
