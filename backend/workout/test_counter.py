#!/usr/bin/env python
import time

num_sets = 2
num_reps = 3
name_exercise = "Test"
time_load = 7
time_pause = 3
time_pause_set = 53

for set in range(1,1+num_sets):
    print (set)
    print(name_exercise)

    for rep in range(1,1+num_reps):
        print (" "+str(rep))
        print (" Load")
        time.sleep(time_load)

        print (" Pause")
        time.sleep(time_pause)

    print ("Set pause")
    time.sleep(time_pause_set)
