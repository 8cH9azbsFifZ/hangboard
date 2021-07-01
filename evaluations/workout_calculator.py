##https://beastfingersclimbing.com/training/workout

"""
WORKOUT LOAD AND FREQUENCY
Research from the University of London has shown that training at 70-80% of 1RM elicits an significant increase in tendon force, torque transfer and absolute strength (link here). Remember to not use thumb-locking when half crimping. Never train at 100%. 1-2 times a week.

REST BETWEEN REPS/SETS
Moderate & Easy
Reps rest: 1-2 seconds
Sets rest: 1-2 minute
For Intense
Reps rest: 5-10 seconds
Sets rest: 2-5 minutes
PERIODIZATION
Loading sessions are planned in high-load sessions, and low-load sessions, also reffered to as de-loading sessions. For example, training in a 4 week block is a safe way to prevent injury. 1 week training at 60% of load, 2nd week at 70% load, 3rd week 80% load, and then back down to 60% load. After 4 weeks you can retest your max, and then re-adjust your percentages to your new 1 rep max onr-arm hang.
Every climber is different and everyone advances at different rates, we've seen climbers advance at 2-5 Lbs a month, and have seen some advance at 8-10lbs a month. Don't rush, focus on your rest, nutrition, recovery.

WARM-UP
Warm-up should last for 30 minutes. If you don't have time to calculate your max hang, you can base it off of what your climbing in correlation to your bodyweight using our calculator (here). Warm up at 50% of the MVC listed (.5 x MVC), and lift 4 sets of 10 reps. Mixing in push-ups, or pull-ups at 3 sets of 7 can also be helpful. If climbing, you can warm-up on easy climbing.


EASY
(50% MAX)
10 reps,
4 sets
5 sec. holds
MODERATE
(70% MAX)
7 reps,
3 sets,
5 sec. holds
INTENSE
(90% MAX)
5 reps,
3 sets,
3 sec. holds


"""

def _create_easy_workout(mvc):
    intensity = 0.5
    loadmax = intensity * mvc
    reps = 10
    sets = 4
    count = 5
    wa = '{ "Name": "Easy", "Session": 1, "ID": "WMVC-EASY-1", "Sets": ['
    for i in range(0,sets):
        wa = wa + '\n{ "Rest-to-Start": 120, "Exercise": "1 Hand Pull", "Counter": '+str(count)+', "Pause": 2, "Reps": '+str(reps)+', "Left": "20mm", "Right": "20mm", "Type": "1 Hand Pull", "Intensity": '+str(intensity)+'}'
        if i <sets-1:
            wa = wa + ","
    wa = wa + ']}'
    return wa

def _create_moderate_workout(mvc):
    intensity = 0.7
    loadmax = intensity * mvc
    reps = 7
    sets = 3
    count = 5
    wa = '{ "Name": "Moderate", "Session": 1, "ID": "WMVC-MODERATE-1", "Sets": ['
    for i in range(0,sets):
        wa = wa + '\n{ "Rest-to-Start": 120, "Exercise": "1 Hand Pull", "Counter": '+str(count)+', "Pause": 2, "Reps": '+str(reps)+', "Left": "20mm", "Right": "20mm", "Type": "1 Hand Pull", "Intensity": '+str(intensity)+'}'
        if i <sets-1:
            wa = wa + ","
    wa = wa + ']}'
    return wa

def _create_intense_workout(mvc):
    intensity = 0.9
    loadmax = intensity * mvc
    reps = 5
    sets = 3
    count = 3
    wa = '{ "Name": "Intense", "Session": 1, "ID": "WMVC-INTENSE-1", "Sets": ['
    for i in range(0,sets):
        wa = wa + '\n{ "Rest-to-Start": 300, "Exercise": "1 Hand Pull", "Counter": '+str(count)+', "Pause": 10, "Reps": '+str(reps)+', "Left": "20mm", "Right": "20mm", "Type": "1 Hand Pull", "Intensity": '+str(intensity)+'}'
        if i <sets-1:
            wa = wa + ","
    wa = wa + ']}'
    return wa



mvc = 48
wa = '{ "Workouts": ['
wa = wa + _create_easy_workout(mvc) + ","
wa = wa + _create_moderate_workout(mvc) + ","
wa = wa + _create_intense_workout(mvc)
wa = wa + ']}'

print (wa)