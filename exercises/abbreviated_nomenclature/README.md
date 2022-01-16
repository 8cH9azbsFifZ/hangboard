# Abbreviated nomenclature for smart timer creation

 
# Standard
* square brackets [optional option]
* angle brackets <required argument>
* curly braces {default values}
* parenthesis (miscellaneous info)

* Reference: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html

# Abbreviated syntax
2x 3x Hang @25mm +0kg #4;Open 7(3)s:57s
2x      3x      Hang       @18mm              4        Crimp  0             7                    3               60
[#sets] <#reps> <Exercise> <Hold[left;right]> [Finger] [Grip] [AddedWeight] <HangTime[(Margin)]> <PauseRepTime> [PauseSetTime]

2x 3x Hang @18mm &4 §Crimp W+5kg 7:3:60s

2x 7x Hang @Jug 7:3:150s
2x 7x Hang @45mm &Front3 §Open 7:3:150s
2x 7x Hang @45mm &4 §Open 7:3:150s


3x MEDHang @18mm 7(3):180s
3x MAXHang @30mm W+10kg 7(3):180s

Not implemented yet: ranges...
4-8x SubHangsMED @30mm 20-45:30-120s



# Lopez for reference
+ 3 x MEDHangs x 15"(5):3'
    + 3 times
    + Exercise MED Hangs
    + 15 seconds hang time
    + 5 seconds margin
    + 3 minutes rest time
+ Means: reps = 1, sets = 3
+ Edge size dynamically found

# JSON format for reference
{ "Rest-to-Start": 5,       
"Exercise": "Hang", 			    
"Counter": 12, 	
"Pause": 180,    
"Reps": 5, 
"Left": "15mm", 
"Right": "15mm", 
"Description": "Do a 12-second hang using a feature that you can barely hold for 15 seconds with maximum effort.",
"No": 1, 
"Fingers": 4, 
"Grip": "Open", 
"Type": "Hang",
"Intensity": 0.35
}


# Warmup Routine for Reference
5x Hang @Jug 10:20:60s
5x 4xPullup @Jug 0:20:60s
5x Hang @30mm 10:20:120s
5x 5xPullup @30mm 0:30s