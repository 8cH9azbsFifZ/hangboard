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

class ExerciseParser():
    def __init__(self, exercise_string=""):
        self._exercise_string = exercise_string

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

        print (self._exercise_string)

        self._parse()

        print (self.Exercise)

    def _parse(self):
        pattern = re.compile("^([0-9]+x) ([0-9]+x) ")
        i0 = 0 # index zero (could be 1 if first word is a set)
        stmp = self._exercise_string.split()

        if pattern.match (self._exercise_string):
            print ("Contains a set counter")
            i0 = 1
            self.Exercise["Sets"] = int(stmp[0].replace("x",""))
            
        self.Exercise["Reps"] = int(stmp[i0].replace("x",""))
        self.Exercise["Type"] = stmp[i0+1]
        if ";" in stmp[i0+2]:
            print ("Contains left/right holds")
            self.Exercise["Left"] = stmp[i0+2].split(";")[0].replace("@","")
            self.Exercise["Right"] = stmp[i0+2].split(";")[1]
        else:
            self.Exercise["Left"] = stmp[i0+2].replace("@","")
            self.Exercise["Right"] = self.Exercise["Left"]

        if "&" in stmp[i0+3]:
            print ("Contains finger")
            self.Exercise["Finger"] = stmp[i0+3].replace("&","")

        if "§" in stmp[i0+4]:
            print ("Contains grip")
            self.Exercise["Grip"] = stmp[i0+4].replace("§","")

        if "W" in stmp[i0+5]:
            print ("Contains added weight")
            self.Exercise["AddedWeight"] = float(stmp[i0+5].replace("W","").replace("kg",""))

        tt = stmp[i0+6].replace("s","").split(":")
    
        if "(" in tt[0]:
            print ("Contains margin")
            self.Exercise["Hangtime"] = int(tt[0].split("(")[0].replace("(","").replace(")",""))
            self.Exercise["HangtimeMargin"] = int(tt[0].split("(")[1].replace(")",""))
        else:
            self.Exercise["Hangtime"] = int(tt[0].replace("(","").replace(")",""))

        self.Exercise["PauseRepTime"] = int(tt[1])

        if len(tt) == 3:        
            self.Exercise["PauseSetTime"] = int(tt[2])

if __name__ == "__main__":
    tmp = "2x 3x Hang @18mm &4 §Crimp W+5kg 7:3:60s"
    e = ExerciseParser(exercise_string=tmp)

    tmp = "3x 4xPullUp @18mm;19mm &4 §Crimp W+5kg 7(2):3:60s"
    e = ExerciseParser(exercise_string=tmp)
