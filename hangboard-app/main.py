from flask import Flask, render_template, request, Response
import time

app = Flask(__name__) 

@app.route("/", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Encrypt') == 'Encrypt':
            # pass
            print("Encrypted")
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
		x = 0

		while x <= 100:
			yield "data:" + str(x) + "\n\n"
			x = x + 10
			time.sleep(0.5)

	return Response(generate(), mimetype= 'text/event-stream')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
