from crypt import methods
from flask import Flask, request
import json
from urllib.request import urlopen

app = Flask(__name__)

## Read file
#file_workout = "./workouts.json"
#file_exercises = "./exercises.json"
# with open (file_workout) as json_file:
#     workouts = json.load(json_file)
# with open (file_exercises) as json_file:
#     exercises = json.load(json_file)

## Read url
url_workout = "https://raw.githubusercontent.com/8cH9azbsFifZ/hangboard/dev/exercises/json-exercises/workouts.json"
url_exercises = "https://raw.githubusercontent.com/8cH9azbsFifZ/hangboard/dev/exercises/json-exercises/exercises.json"
response_workout = urlopen(url_workout)
response_exercises = urlopen(url_exercises)
workouts = json.loads(response_workout.read())
exercises = json.loads(response_exercises.read())



def display_workouts(short=0):
    i = 0
    res = ""
    res_short = {"workouts": []}
    for w in workouts["workouts"]:
        i += 1
        res = res + "<br/>\n" + "{} {}".format(i, w["workout_name"])
        w_short = {}
        for k in ["workout_name", "duration"]:
            w_short [k] = w[k]
        res_short["workouts"].append(w_short) 
    print (res)
    print (res_short)
    if short == 1:
        return (res_short)
    return (res)

def display_workout():
    nw = 2
    res = ""
    print (workouts["workouts"][nw]["workout_name"])
    for e in workouts["workouts"][nw]["exercises"]:
        for ee in exercises["exercises"]:
            if ee["exercise_name"] in e["exercise_name"]:
                break
        if "time_exercise" in e:
            time_exercise = e["time_exercise"]
            time_pause = e["time_pause"]
            res = res + "<br/>\n" + "{} {} {} {} {} <img src={}>".format(e["sets"],e["reps"], e["exercise_name"],time_exercise,time_pause,e["time_pause_set"],ee["url_image"])
        else:
            res = res + "<br/>\n" + "{} {} {} {} <img src={}> ".format(e["sets"],e["reps"], e["exercise_name"],e["time_pause_set"],ee["url_image"])
    print (res)
    return (res)

@app.route('/')
def page_main():
    return ("Test")

@app.route('/workout')
def page_workout():
    a = display_workout()
    return (a)

@app.route('/workouts')
def page_workouts():
    short = request.args.get("short", default = 0, type=int)
    a = display_workouts(short)

    return (a)

@app.route('/workouts1')
def page_workouts2():
    short = 1
    a = display_workouts(short)

    return (a)

@app.route('/api', methods=['POST'])
def returnapi():
    short = request.form.get("short", default=0, type=int)
    a = display_workouts(short)
    return (a)
