#!/usr/bin/env pyhton
from flask import Flask
import json

file_workout = "./workouts.json"
file_exercises = "./exercises.json"

app = Flask(__name__)

with open (file_workout) as json_file:
    workouts = json.load(json_file)

with open (file_exercises) as json_file:
    exercises = json.load(json_file)

def display_workouts():
    i = 0
    res = ""
    for w in workouts["workouts"]:
        i += 1
        res = res + "<br/>\n" + "{} {}".format(i, w["workout_name"])
    print (res)
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
    a = display_workouts()
    return (a)
