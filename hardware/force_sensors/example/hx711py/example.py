#! /usr/bin/python2

import time
import sys

EMULATE_HX711=False

referenceUnit = 1
referenceUnit = 17145


if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()


#    def __init__(self, dout, pd_sck, gain=128):

#hx = HX711(5, 6)
GPIO.setmode(GPIO.BCM)
#hx = HX711(11, 13)
hx = HX711(17, 27)
# https://raspi.tv/2013/rpi-gpio-basics-4-setting-up-rpi-gpio-numbering-systems-and-inputs
# sodass die 17 und 27 verwendet werden




"""

The hx711 outputs a value corresponding to the ratio of difference voltage divided by the voltage applied to the load cell. This ratio is factored by the gain. Full scale output is 800000 to 7FFFFF in hexadecimal and corresponds to 0.5 to - 0.5 difference ratio V/V. The load cell calibration certificate tells me the output at a particular voltage with a defined load applied. My certificate says 1.996 mV at 5 V with 50 kg applied. The difference ratio is then 0.0003992 V/V at 50 kg. I am using a gain of 128 so this difference ratio becomes 0.0511 V/V. This is then 10.2 % of the full scale 0.5 V and will correspond to 800000 x 10.2 % in hexadecimal. This will be a decimal value of 857275 for 50 kg. The sensitivity is therefore 17145 per kg.
"""

scalefactor=1/17145.0


# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        val = hx.get_weight(5)
        print(val)

        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #print "A: %s  B: %s" % ( val_A, val_B )

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
