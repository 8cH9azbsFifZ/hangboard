import importlib.util
spec = importlib.util.spec_from_file_location("Database", "../backend/database.py")
foo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foo)
#from ../backend/database import Database

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def plot_load(t,load):
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_title("Load")    
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('Load (kg)')
	ax1.plot(t,load, c='r', label='Last Rep')
	leg = ax1.legend()
	#plt.show()
	plt.savefig("Load.png")

def _scribbel():
    timemax=data["time"].max()
    last20minutes=timemax-60*4
    lc=data["loadcurrent"]>25
    l20m=data["time"]>last20minutes
    #print (data["loadcurrent"])
    #print (data[lc][l20m]["loadcurrent"])
    l20m_maxload = data[lc][l20m]["loadmaximal"].max()
    print (l20m_maxload)
    #plot_load(data[lc][l20m]["time"],data[lc][l20m]["loadcurrent"])
    #print(l20m_maxload)
    #print (d._get_user_bodyweight())
    print (d._get_maxload(hold="20mm"))
    #print (d._get_maxload(hold="20mm",hand="left"))
    #print (d._get_maxload())


    # Testing intensity
    maxload = d._get_maxload(hold="20mm")
    intensity_strength = 0.9
    intensity_endurance = 0.6
    intensity_endurance_low = 0.3
    load_strength = intensity_strength * maxload
    load_endurance = intensity_endurance * maxload
    load_endurance_low = intensity_endurance_low * maxload

    print (load_strength) 
    print (load_endurance)
    print (load_endurance_low)
    
    plot_load(data[lc][l20m]["time"],data[lc][l20m]["loadcurrent"])
    derivative = np.diff (data[lc][l20m]["loadcurrent"]) / np.diff(data[lc][l20m]["time"])
    derivative2 = np.diff (derivative) 
    tt = data[lc][l20m]["time"]
    #ttt=np.delete(tt,1)
    #np.append(derivative, 0)
    print (derivative)
    #plot_load(tt,derivative)
    np.savetxt("out.txt", derivative2)#data[lc][l20m]["loadcurrent"])


if __name__ == "__main__":
    d = foo.Database(hostname="hangboard", user="root", password="rootpassword")
    d._set_user(uuid="us3r")
    d._get_maxload()
    data = pd.DataFrame(list(d._coll_raw.find()))
    dtime = np.diff(data["time"])
    timebetweensessions = 360.01
    seltime = abs(dtime)>timebetweensessions
    seltime1 = np.append(False,seltime)
    seltime2 = np.roll(seltime1,1)
    #minimaltimebetweensessions = 3600 * 48
    #print(minimaltimebetweensessions)
    #print (dtime[seltime])
    #print (data[seltime1]["time"])
    d0=0
    d1=1
    for d in data[seltime1]["time"]:
        dd=datetime.fromtimestamp(d).strftime("%A, %B %d, %Y %I:%M:%S")
        print (dd)
    for d in data[seltime2]["time"]:
        dd=datetime.fromtimestamp(d).strftime("%A, %B %d, %Y %I:%M:%S")
        print (dd)
    for d in data["time"]:
        d0=d1
        d1=d
        if d>0:
            dd=datetime.fromtimestamp(d).strftime("%A, %B %d, %Y %I:%M:%S")
            #print (str(d1-d0) + " "+ str(d)+ " "+str(dd))