from flask import Flask, render_template, request, Response, redirect, url_for, session

app = Flask(__name__) 
app.secret_key = "test"

@app.route("/")
def index():
    print(request.method)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
