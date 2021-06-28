from database import Database
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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

if __name__ == "__main__":
    d = Database(hostname="hangboard", user="root", password="rootpassword")
    d._set_user(uuid="us3r")
    d._get_maxload()
    print (d._coll_raw)
    data = pd.DataFrame(list(d._coll_raw.find()))
    print (data)
    timemax=data["time"].max()
    last20minutes=timemax-60*1
    lc=data["loadcurrent"]>0
    l20m=data["time"]>last20minutes
    print (data["loadcurrent"])
    print (data[lc][l20m]["loadcurrent"])
    l20m_maxload = data[lc][l20m]["loadcurrent"].max()
    plot_load(data[lc][l20m]["time"],data[lc][l20m]["loadcurrent"])
    print(l20m_maxload)


