from flask import Flask, render_template, request, Response
import time
import json
#from hx711 import HX711

app = Flask(__name__) 


def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

def pbar(sec, what):
    items = range (1, 1+sec)
    for item in progressBar(items, prefix = what, suffix = 'Complete - ' + str(sec) + " seconds total", length = 50):
        time.sleep (.1)

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
    
    def run_exercise (self): 
        e = self.session["Exercise"][self.current_exercise]
        self.current_exercise_name = e["Type"]
        self.current_exercise_reps_counter = 0
        self.current_exercise_reps_total = e["Reps"]
        self.current_exercise_duration = e["Counter"]
        self.current_exercise_counter = 0
        self.current_exercise_rest_to_start = e["Rest-to-Start"]
        #pbar (rest_to_start, "Rest to start - upcoming " + e["Type"])
        for r in range (1, 1+e["Reps"]):
                        start_detected = 2
                        if (start_detected == 1):
                            if (e["Type"] == "Hang"):
                                pbar (e["Counter"], e["Type"])
                            elif (e["Type"] == "Maximal Hang"):
                                print (e["Type"] + "Key press?")
                            elif (e["Type"] == "Assisted Pull Ups"):
                                print (e["Type"] + "Key press?")
                                #pbar (e["Counter"], e["Type"])
                            else:
                                print ("Key press?")

                            pbar (e["Pause"], "Pause")


ex = Exercise()
ex.run_exercise()

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
    return render_template("index.html", Exercise_Name = ex.current_exercise_name, Current_Exercise = ex.current_exercise, Total_Exercises = ex.total_exercises)

@app.route('/progress')
def progress():
    def generate():
        x = 0
        #x = ex.session["Exercise"][0]["Rest-to-Start"]

        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(.11)

    
    return Response(generate(), mimetype= 'text/event-stream')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
