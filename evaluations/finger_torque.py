import math
load = 78.7 # kg (-> normalized to weight)
hold_depth = 33 #mm 
hangtime = 10 #s
hold_angle = 0 #°

def calc_finger_intensity (load, hold_depth, hold_angle, time):
    finger_intensity = load * time / (hold_depth*math.cos (hold_angle))
    return finger_intensity


print (calc_finger_intensity(94, 33, 0, 10))
print (calc_finger_intensity(68, 20, 0, 10))
print (calc_finger_intensity(78, 50, 20, 10))
