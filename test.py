#!/usr/bin/python3

# sudo apt-get install -y python3-pip
# pip3 install HX711 RPi.GPIO
#from hx711 import HX711

import json
import time

def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

def pbar(sec, what):
    items = range (1, 1+sec)
    for item in progressBar(items, prefix = what, suffix = 'Complete - ' + str(sec) + " seconds total", length = 50):
        time.sleep (.1)
  
# Opening JSON file
with open('test.json') as json_file:
    data = json.load(json_file)
    session = (data["Sessions"][0])

    print (session["Name"])
    for e in session["Exercise"]:
        rest_to_start = e["Rest-to-Start"]
        pbar (rest_to_start, "Rest to start - upcoming " + e["Type"])

        for r in range (1, 1+e["Reps"]):
            start_deteced = 1
            if (start_detected):
                if (e["Type"] == "Hang"):
                    pbar (e["Counter"], e["Type"])
                elif (e["Type"] == "Maximal Hang"):
                    print (e["Type"] + "Key press?")
                elif (e["Type"] == "Assisted Pull Ups"):
                    print (e["Type"] + "Key press?")
                    #pbar (e["Counter"], e["Type"])
                else:
                    print ("Key press?")

            pbar (e["Pause"], "Pause")


#try:
#    hx711 = HX711(
#    dout_pin=5,
#    pd_sck_pin=6,
#    channel='A',
#    gain=64
#    )
#
#    hx711.reset()   # Before we start, reset the HX711 (not obligate)
#    measures = hx711.get_raw_data(num_measures=3)
#finally:
#    GPIO.cleanup()  # always do a GPIO cleanup in your scripts!
#
#print("\n".join(measures))
