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

---
Test
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

        # Parse counters for set and rep
        if pattern.match (self._exercise_string):
            print ("Contains a set counter")
            t = self._exercise_string.split("x")
            s = t[0]
            self.Exercise["Sets"] = s
            r = t[1]
            self.Exercise["Repts"] = r

        else:
            r = self._exercise_string.split("x")[0]
            self.Exercise["Reps"] = r
    

if __name__ == "__main__":
    tmp = "2x 3x Hang @18mm &4 §Crimp W+5kg 7:3:60s"
    e = ExerciseParser(exercise_string=tmp)


    tmp = "3x Hang @18mm &4 §Crimp W+5kg 7:3:60s"
    e = ExerciseParser(exercise_string=tmp)
