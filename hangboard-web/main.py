from flask import Flask, render_template, request, Response, session

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
