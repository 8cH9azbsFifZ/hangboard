"""
This file contains the code for the initial sensor data plot generators.
"""

import numpy as np
import matplotlib.pyplot as plt
import json


fname="sample_force_hang_left_right_slowpull_fastpull.txt"
loadthresh = 2.0
with open(fname) as f:
	lines = f.readlines()
	t0=1623842395.41
	n = len(lines)
	print (n)
	t = []
	load = []
	loadavg = []
	fti = []
	loadmax = []
	rfd = []
	loadloss = []
	for i in range (0,n-1):
		tmpload = float(lines[i].split()[5])
		if (tmpload > loadthresh):
			t.append(float(lines[i].split()[3]) - t0)
			load.append(tmpload)
			loadavg.append(float(lines[i].split()[8]))
			fti.append(float(lines[i].split()[11]))
			loadmax.append(float(lines[i].split()[14]))
			rfd.append(float(lines[i].split()[16]))
			loadloss.append(float(lines[i].split()[18]))
	print ("selected " + str(len(t)))
	#t = [float(line.split()[3])-t0 for line in lines] 
	#load = [float(line.split()[5]) for line in lines]
	#loadavg = [float(line.split()[8]) for line in lines]
	#fti = [float(line.split()[11]) for line in lines]
	#loadmax = [float(line.split()[14]) for line in lines]
	#rfd = [float(line.split()[16]) for line in lines]
	#loadloss = [float(line.split()[18]) for line in lines]

print ("Create simulation data")
list = json.dumps({"SimulationData": {
	"time": t, "load": load, "loadavg": loadavg, "fti": fti, "loadmax": loadmax, "rfd": rfd, "loadloss": loadloss
	}})
with open('simulation_data.json', 'w', encoding='utf-8') as f:
    json.dump(list, f, ensure_ascii=False, indent=4)

for i in range (0,len(t)-1):
	print ('FlSpot(%.2f, %.2f),' %(t[i],load[i]))

def plot_load():
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_title("Load (Hang, Left Pull, Right Pull, Slow Pullup, Fast Pullup)")    
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('Load (kg)')
	ax1.plot(t,load, c='r', label='Test 1')
	leg = ax1.legend()
	#plt.show()
	plt.savefig("Load.png")

def plot_loadavg():
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_title("Load (Hang, Left Pull, Right Pull, Slow Pullup, Fast Pullup)")    
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('Average Load (kg)')
	ax1.plot(t,loadavg, c='r', label='Test 1')
	leg = ax1.legend()
	#plt.show()
	plt.savefig("LoadAvg.png")

def plot_fti():
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_title("Load (Hang, Left Pull, Right Pull, Slow Pullup, Fast Pullup)")    
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('FTI')
	ax1.plot(t,fti, c='r', label='Test 1')
	leg = ax1.legend()
	#plt.show()
	plt.savefig("FTI.png")

def plot_loadmax():
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_title("Load (Hang, Left Pull, Right Pull, Slow Pullup, Fast Pullup)")    
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('Maximal Load (kg)')
	ax1.plot(t,loadmax, c='r', label='Test 1')
	leg = ax1.legend()
	#plt.show()
	plt.savefig("LoadMax.png")

def plot_rfd():
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_title("Load (Hang, Left Pull, Right Pull, Slow Pullup, Fast Pullup)")    
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('RFD')
	ax1.plot(t,rfd, c='r', label='Test 1')
	leg = ax1.legend()
	#plt.show()
	plt.savefig("RFD.png")

def plot_loadloss():
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_title("Load (Hang, Left Pull, Right Pull, Slow Pullup, Fast Pullup)")    
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('Load Loss')
	ax1.plot(t,loadloss, c='r', label='Test 1')
	leg = ax1.legend()
	#plt.show()
	plt.savefig("LoadLoss.png")

plot_load()
plot_loadavg()
plot_fti()
plot_loadmax()
plot_rfd()
plot_loadloss()