import math
load = 78.7 # kg (-> normalized to weight)
hold_depth = 33 #mm 
hangtime = 10 #s
hold_angle = 0 #°

def estimate_tendon_intensity (load=100, hold_depth=50, hold_angle=0, time=10):
    """
    Try to estimate the intensity of an exercise for the tendons.
    JUG = 50 mm (whole finger used)
    """
    tendon_intensity = load * time / (hold_depth*math.cos (hold_angle))
    return tendon_intensity

print (estimate_tendon_intensity(load=78)) # simple hang
print (estimate_tendon_intensity(load=94)) # weigthed hang
print (estimate_tendon_intensity(68, 20, 0, 10)) # 20mm mvc hang
print (estimate_tendon_intensity(78, 50, 20, 10)) # sloper hang
