#!/usr/bin/env python
import pyparsing as pp

greet = pp.Word(pp.alphas) + "," + pp.Word(pp.alphas) + "!"
for greeting_str in [
            "Hello, World!",
            "Bonjour, Monde!",
            "Hola, Mundo!",
            "Hallo, Welt!",
        ]:
    greeting = greet.parse_string(greeting_str)
    #print(greeting)


t1 = '2x 3x Hang @25mm +0kg #4;Open 7(3)s:57s' 
t2=t1 #"1   x y asdf asdf"
tmp = pp.Word(pp.nums)+"x"+pp.Word(pp.nums)+"x"+pp.Word(pp.alphas)+pp.Optional("@"+pp.Word(pp.alphanums))+pp.Optional("+"+pp.Word(pp.nums)+"kg") \
    +pp.Optional('#'+pp.Word(pp.alphanums)+";"+pp.Word(pp.alphanums))+pp.Word(pp.nums)+"("+pp.Word(pp.nums)+")s:"+pp.Word(pp.nums)+"s"

x1 = tmp.parse_string(t2)

print (x1)
num_sets = x1[0]
num_reps = x1[2]
name_exercise = x1[4]
name_hold = x1[6]
added_weight = x1[8]
name_fingers = x1[11]
name_grip = x1[13]
time_load = x1[14]
time_pause = x1[16]
time_pause_set = x1[18]
print (num_sets, num_reps, name_exercise, name_hold, added_weight, name_fingers, name_grip, time_load, time_pause, time_pause_set)