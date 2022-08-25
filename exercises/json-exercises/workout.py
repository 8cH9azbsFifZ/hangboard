#!/usr/bin/env pyhton
import json

file_workout = "./workouts.json"

with open (file_workout) as json_file:
    data = json.load(json_file)

i = 0
for w in data["workouts"]:
    i += 1
    print (i, w["workout_name"])

nw = 2
print (data["workouts"][nw]["workout_name"])
for e in data["workouts"][nw]["exercises"]:
    if "time_exercise" in e:
        time_exercise = e["time_exercise"]
        time_pause = e["time_pause"]
        print (e["sets"],e["reps"], e["exercise_name"],time_exercise,time_pause,e["time_pause_set"])
    else:
        print (e["sets"],e["reps"], e["exercise_name"],e["time_pause_set"])
