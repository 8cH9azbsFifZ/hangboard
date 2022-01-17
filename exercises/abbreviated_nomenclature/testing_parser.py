#!/usr/bin/env python
"""
[#sets] <#reps> <Exercise> <Hold[left;right]> [Finger] [Grip] [AddedWeight] <HangTime[(Margin)]> <PauseRepTime> [PauseSetTime]
Examples:
2x 3x Hang @18mm &4 §Crimp W+5kg 7:3:60s
2x 7x Hang @Jug 7:3:150
2x 7x Hang @45mm &Front3 §Open 7:3:150
2x 7x Hang @45mm &4 §Open 7:3:150
3x MEDHang @18mm 7(3):180
3x MAXHang @30mm W+10kg 7(3):180

"""

import re
import logging
import time
import json
import paho.mqtt.client as mqtt
logging.basicConfig(level=logging.DEBUG, format='Counter(%(threadName)-10s) %(message)s', )

class Exercise():
    def __init__(self):
        self.Exercise = {}
        self.Exercise["Sets"] = 1
        self.Exercise["Reps"] = 1
        self.Exercise["Type"] = "Hang"
        self.Exercise["Left"] = "Jug"
        self.Exercise["Right"] = "Jug"
        self.Exercise["Finger"] ="4"
        self.Exercise["Grip"] = "Jug"
        self.Exercise["AddedWeight"] = "0kg"
        self.Exercise["Hangtime"] = 7
        self.Exercise["HangtimeMargin"] = 5
        self.Exercise["PauseRepTime"] = 53
        self.Exercise["PauseSetTime"] = 0


class Workout(): # FIXME: pass default values
    def __init__(self):
        self.Workout = {}
        self.Workout["Reference"] = "Generated from abbreviated text"
        self.Workout["Author"] = "Python"
        self.Workout["URL"] = ""
        self.Workout["Workouts"] = []

        self._workout = {}
        self._workout["ID"] = "TMP-ID-1"
        self._workout["Name"] = "Test1"
        self._workout["Sets"] = []

        self.Workout["Workouts"].append(self._workout)


class ExerciseParser():
    def __init__(self, exercise_string=""):
        self._exercise_string = exercise_string

        self._exercise = Exercise()
        self.Exercise = self._exercise.Exercise

        print (self._exercise_string)
        self._parse()
        print (self.Exercise)

    def _parse(self):
        pattern = re.compile("^([0-9]+x) ([0-9]+x) ")
        i0 = 0 # index zero (could be 1 if first word is a set)
        stmp = self._exercise_string.split()

        if pattern.match (self._exercise_string):
            logging.debug ("Contains a set counter")
            i0 = 1
            self.Exercise["Sets"] = int(stmp[0].replace("x",""))
            
        self.Exercise["Reps"] = int(stmp[i0].replace("x",""))
        self.Exercise["Type"] = stmp[i0+1]
        if ";" in stmp[i0+2]:
            logging.debug ("Contains left/right holds")
            self.Exercise["Left"] = stmp[i0+2].split(";")[0].replace("@","")
            self.Exercise["Right"] = stmp[i0+2].split(";")[1]
        else:
            self.Exercise["Left"] = stmp[i0+2].replace("@","")
            self.Exercise["Right"] = self.Exercise["Left"]

        if "&" in stmp[i0+3]:
            logging.debug ("Contains finger")
            self.Exercise["Finger"] = stmp[i0+3].replace("&","")

        if "§" in stmp[i0+4]:
            logging.debug ("Contains grip")
            self.Exercise["Grip"] = stmp[i0+4].replace("§","")

        if "W" in stmp[i0+5]:
            logging.debug ("Contains added weight")
            self.Exercise["AddedWeight"] = float(stmp[i0+5].replace("W","").replace("kg",""))

        tt = stmp[i0+6].replace("s","").split(":")
    
        if "(" in tt[0]:
            logging.debug ("Contains margin")
            self.Exercise["Hangtime"] = int(tt[0].split("(")[0].replace("(","").replace(")",""))
            self.Exercise["HangtimeMargin"] = int(tt[0].split("(")[1].replace(")",""))
        else:
            self.Exercise["Hangtime"] = int(tt[0].replace("(","").replace(")",""))

        self.Exercise["PauseRepTime"] = int(tt[1])

        if len(tt) == 3:        
            self.Exercise["PauseSetTime"] = int(tt[2])


    def _create_workout_json(self):
        self._set = {}
        self._set["Rest-to-Start"] = 0 # FIXME Set pause afterwards must be implemented in workout
        self._set["Exercise"] = self.Exercise["Type"]
        self._set["Counter"] = self.Exercise["Hangtime"]
        self._set["Pause"] = self.Exercise["PauseRepTime"]
        self._set["Reps"] = self.Exercise["Reps"]
        self._set["Left"] = self.Exercise["Left"]
        self._set["Right"] = self.Exercise["Right"]
        self._set["Fingers"] = self.Exercise["Finger"]
        self._set["Grip"] = self.Exercise["Grip"]
        self._set["AddedWeight"] = self.Exercise["AddedWeight"]

        self._workout = Workout()
        for i in range(0,self.Exercise["Sets"]):
            self._workout.Workout["Workouts"][0]["Sets"].append(self._set)

        return self._workout

class WorkoutCounter():
    def __init__(self, workout=Workout()):
        self._workout = workout
        self._sets = self._workout.Workout["Workouts"][0]["Sets"] # FIXME: 1 workout per file
        self._is_pause = False 
        self.reset()

    def reset(self):
        self.Counter = {}
        self.Counter["CounterSet"] = 1
        self.Counter["CounterRep"] = 0
        self.Counter["CounterSleep"] = 0
        self.Counter["SetsTotal"] = len(self._sets)
        self.Counter["SetExercise"] = self._sets[ 0 ]["Exercise"] 
        self.Counter = {**self.Counter, **self._sets[ 0 ]}

    def __next__(self): 
        if self.Counter["SetsTotal"] == 0:
            logging.debug ("No sets") 
            return -1
        
        if not self._is_pause:  # If exercise (not pause) state
            self._is_pause = True # toggle state
            if self.Counter["CounterSet"] <= self.Counter["SetsTotal"]: 
                self.Counter["RepsTotal"] = self._sets[ self.Counter["CounterSet"]-1 ]["Reps"]
                self.Counter["SetExercise"] = self._sets[ self.Counter["CounterSet"]-1 ]["Exercise"] 
                self.Counter = {**self.Counter, **self._sets[ self.Counter["CounterSet"]-1 ]}
                if self.Counter["CounterRep"] < self.Counter["RepsTotal"]:
                    self.Counter["CounterRep"] = self.Counter["CounterRep"] + 1
                else:
                    self.Counter["CounterRep"] = 1        
                    self.Counter["CounterSet"] = self.Counter["CounterSet"] + 1
            else:
                if self.Counter["CounterRep"] < self.Counter["RepsTotal"]:
                    self.Counter["CounterRep"] = self.Counter["CounterRep"] + 1
                else:
                    return -1
            self.Counter["Exercise"] = self.Counter["SetExercise"]
            self.Counter["CounterSleep"] = self.Counter["Counter"]
            return self.Counter
        else: # If pause (not exercise) state
            self._is_pause = False # toggle state
            self.Counter["Exercise"] = "Pause"
            self.Counter["CounterSleep"] = self.Counter["Pause"]
            return self.Counter

class WorkoutLooper():
    def __init__(self, workout=Workout()):
        self._wc = WorkoutCounter(workout=workout)
        self._is_pause = False

    def _loop_all(self, stepping=.1): # FIXME
        self._wc.reset()
        while True:
            c = self._wc.Counter
            s = 1
            self._get_input()
            if not self._is_pause:
                c = next(self._wc)
                if c == -1:
                    break
                s = c["CounterSleep"]
            else:
                c["Exercise"] = "WaitForHang"
            self._show_msg (c)
            time.sleep(stepping * s) # WIP FIXME - no events during sleep(!)
    
    def _show_msg(self,msg):
        print(msg)

    def _get_input(self):
        return

class WorkoutMQTT(WorkoutLooper):
    def __init__(self, workout=Workout(), hostname="localhost", port=1883):
        self._hostname = hostname
        self._port = port
        self._samplingrate = 0.01 #blocks for 100ms (or whatever variable given, default 1s)
        self._connect()

        super().__init__(workout=workout) # Inherit from master

        self._reset()

    def _reset(self):
        self._is_pause = True
        self._wc.reset()

    def _show_msg(self,msg): # Override
        logging.debug(msg)
        self._sendmessage(topic="/counter", message=msg)

    def _get_input(self): #Override
        self._client.loop(self._samplingrate) 

    def _connect(self):
        # Connect to MQTT
        self._client = mqtt.Client("Workout")
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(self._hostname, self._port, 60)
        self._sendmessage("/status", "Starting")

    def _sendmessage(self, topic="/none", message="None"):
        self._client.publish("hangboard/workout"+topic, str(message))

    def _on_connect(self, client, userdata, flags, rc):
        logging.debug ("Connected with result code "+str(rc))
        self._client.subscribe("hangboard/workout/control")
        self._client.subscribe("hangboard/sensor/load/loadstatus")

    def _on_message(self, client, userdata, msg):
        logging.debug(">MQTT: " + msg.payload.decode())
        
        # Controls
        #if msg.topic == "hangboard/workout/control":
            #if msg.payload.decode() == "Stop":
            #    #time.sleep(10)
            #    self._workout_running = False
            #    #exit()
            #if msg.payload.decode() == "Start":
            #    self._workout_running = True
            #    next(self._counter)
            #if msg.payload.decode() == "Restart":
            #    self._workout_running = True
            #    self._counter = Counter(self._workout, hostname=self._hostname)
            #if msg.payload.decode() == "ListWorkouts":
            #    self._list_workouts()

        # Hang data
        if msg.topic == "hangboard/sensor/load/loadstatus":

            jj = json.loads(msg.payload.decode())
            if jj["HangDetected"] == "True":
                self._is_pause = False
            else:
                self._is_pause = True
            return


if __name__ == "__main__":
    tmp = "2x 3x Hang @18mm &4 §Crimp W+5kg 7:3:60s"
    tmp = "2x 3x 4xPullUp @18mm;19mm &4 §Crimp W+5kg 7(2):3:60s"
    e = ExerciseParser(exercise_string=tmp)
    f = e._create_workout_json()
    #l = WorkoutLooper(workout=f)
    #l._loop_all()
    m = WorkoutMQTT(workout=f,hostname="raspi-hangboard")
    m._loop_all()
