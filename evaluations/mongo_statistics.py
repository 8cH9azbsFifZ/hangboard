"""
This file contains the code for the initial mongodb persistence statistics...
"""

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
    # snipps for use later on
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

class Statistics():
    def __init__(self, dbhostname="hangboard", dbuser="root", dbpassword="rootpassword", user="us3r"):
        self._db = foo.Database(hostname=dbhostname,user=dbuser,password=dbpassword)
        self._db._set_user(uuid=user)

        self._data = pd.DataFrame(list(self._db._coll_raw.find()))

        self._num_sessions = 0
        self._session_statistics = []

        self._detect_sessions()

    def _detect_sessions(self):
        """
        Detect sessions in database
        """
        sel_not_nan = self._data["time"]>1.0
        dtime = np.diff(self._data[sel_not_nan]["time"])
        timebetweensessions = 3600.01
        seltime = dtime>timebetweensessions
        seltime1 = np.append(False,seltime)

        # TODO: do something useful with the information
        self._session_statistics.append({})
        for d in self._data[sel_not_nan][seltime1]["time"]:
            self._num_sessions = self._num_sessions + 1
            self._session_statistics.append({})
            self._session_statistics[self._num_sessions]["Timestamp"] = d
            dd=datetime.fromtimestamp(d).strftime("%A, %B %d, %Y %I:%M:%S")
            self._session_statistics[self._num_sessions]["Date"] = dd
            self._calc_sessions_params(session=self._num_sessions)

        # TODO create selector: for each session
        # TODO calculate hangtime for each session

        #print ("Number of sessions: " + str(self._num_sessions))
        print (self._session_statistics)

    def _calc_sessions_params(self, session=1):
        tstart = self._session_statistics[session]["Timestamp"]
        maxsessiontime = 3*60*60 # 3 hours
        tstop = tstart + maxsessiontime
        sel_tstart = (self._data["time"] > tstart) 
        sel_tstop = (self._data["time"] < tstop)
        sel_data = self._data[sel_tstart][sel_tstop]
        max_load = sel_data["loadmaximal"].max()
        self._session_statistics[session]["MaxLoad"] = max_load


if __name__ == "__main__":
    #d = foo.Database(hostname="hangboard", user="root", password="rootpassword")
    #d._set_user(uuid="us3r")
    #d._get_maxload()

    s=Statistics()

