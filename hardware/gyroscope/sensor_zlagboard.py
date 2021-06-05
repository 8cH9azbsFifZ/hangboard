"""
Zlagboard sensor backend (gyroscope)

Using a kalman filter.

"""

from io import TextIOBase
from Kalman import KalmanAngle
import smbus			#import SMBus module of I2C
import time
import math

import json
import argparse

import asyncio
import websockets

from threading import Thread
import threading


parser = argparse.ArgumentParser(description="Gyroscope Sensor Backend.")
parser.add_argument ('--host')
parser.add_argument ('--port')
args = parser.parse_args()

WSHOST = args.host 
WSPORT = args.port 

class Gyroscope():
	def __init__(self):
		"""
		Initialize gyroscope class with the neccessary variables for the SMBus module (I2C).
		"""
		self.PWR_MGMT_1 = 0x6B
		self.SMPLRT_DIV = 0x19
		self.CONFIG = 0x1A
		self.GYRO_CONFIG = 0x1B
		self.INT_ENABLE = 0x38
		self.ACCEL_XOUT_H = 0x3B
		self.ACCEL_YOUT_H = 0x3D
		self.ACCEL_ZOUT_H = 0x3F
		self.GYRO_XOUT_H = 0x43
		self.GYRO_YOUT_H = 0x45
		self.GYRO_ZOUT_H = 0x47

		self.init_gyro()

		"""
		Parameters for gyroscope sensor sampling delay (delay_measures) 
		and delay for sending the values (delay_sending).
		"""
		self.message = "Started Gyroscope"
		self.delay_measures = 0.005
		self.delay_sending = 0.005

		self.calibration_duration = 10.0
		"""
		Parameter for calibration duration.
		"""

		""" AngleX_NoHang: Calibrated Angle for no hang detection """
		""" AngleX_Hang: Calibrated Angle for hang detection """
		""" HangDetected: Flag whether a hang is detected or not """
		self.AngleX_NoHang = 0 		
		self.AngleX_Hang = 0		
		self.HangDetected = False	
		self.HangStateChanged = False
		"""
		Time for state changes in order to calculate the hang time
		"""
		self.TimeStateChangePrevious = 0
		self.TimeStateChangeCurrent = 0
		self.LastHangTime = 0
		self.LastPauseTime = 0

		# Start running the measurements
		self._run_measure()

	def init_gyro(self):
		"""
		Initialize GPIO BUS
		"""
		print ("Initialize BUS")
		self.bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
		self.DeviceAddress = 0x68   # MPU6050 device address

		self.MPU_Init()

		time.sleep(1)

	def MPU_Init(self):
		"""
		Read the gyro and acceleromater values from MPU6050.
		"""

		#write to sample rate register
		self.bus.write_byte_data(self.DeviceAddress, self.SMPLRT_DIV, 7)

		#Write to power management register
		self.bus.write_byte_data(self.DeviceAddress, self.PWR_MGMT_1, 1)

		#Write to Configuration register
		#Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
		self.bus.write_byte_data(self.DeviceAddress, self.CONFIG, int('0000110',2))

		#Write to Gyro configuration register
		self.bus.write_byte_data(self.DeviceAddress, self.GYRO_CONFIG, 24)

		#Write to interrupt enable register
		self.bus.write_byte_data(self.DeviceAddress, self.INT_ENABLE, 1)


	def read_raw_data(self, addr):
		"""
		Reading raw data from gyroscope
		"""
		#Accelero and Gyro value are 16-bit
		high = self.bus.read_byte_data(self.DeviceAddress, addr)
		low = self.bus.read_byte_data(self.DeviceAddress, addr+1)

		#concatenate higher and lower value
		value = ((high << 8) | low)

		#to get signed value from mpu6050
		if(value > 32768):
				value = value - 65536
		return value

	def init_measurements (self):
		"""
		Initialize measurements.
		"""
		print ("Set initial parameters")
		self.kalmanX = KalmanAngle()
		self.kalmanY = KalmanAngle()

		print ("Read startup parameters")
		self.RestrictPitch = True	#Comment out to restrict roll to +-90deg instead - please read: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf
		self.radToDeg = 57.2957786
		self.kalAngleX = 0
		self.kalAngleY = 0
		#some MPU6050 Registers and their Address

		#Read Accelerometer raw value
		accX = self.read_raw_data(self.ACCEL_XOUT_H)
		accY = self.read_raw_data(self.ACCEL_YOUT_H)
		accZ = self.read_raw_data(self.ACCEL_ZOUT_H)

		#print(accX,accY,accZ)
		#print(math.sqrt((accY**2)+(accZ**2)))
		if (self.RestrictPitch):
			roll = math.atan2(accY,accZ) * self.radToDeg
			pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * self.radToDeg
		else:
			roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * self.radToDeg
			pitch = math.atan2(-accX,accZ) * self.radToDeg
		print(roll)
		self.kalmanX.setAngle(roll)
		self.kalmanY.setAngle(pitch)
		self.gyroXAngle = roll;
		self.gyroYAngle = pitch;
		self.compAngleX = roll;
		self.compAngleY = pitch;

	def detect_hang(self, angle):
		"""
		Detect a hang based on the calibrated hang / no hang angles.
		A state change variable will also be set.
		"""

		oldstate = self.HangDetected
		self.HangDetected = False
		if (self.AngleX_Hang > self.AngleX_NoHang):
			delta = self.AngleX_Hang - self.AngleX_NoHang
			if (angle + delta > self.AngleX_Hang):
				self.HangDetected = True
		else:
			delta = self.AngleX_NoHang - self.AngleX_Hang
			if (angle - delta < self.AngleX_Hang):
				self.HangDetected = True
		
		if (oldstate == self.HangDetected):
			self.HangStateChanged = False
		else:
			self.HangStateChanged = True

			self.TimeStateChangePrevious = self.TimeStateChangeCurrent
			self.TimeStateChangeCurrent = time.time()

			if (self.HangDetected == True):
				self.LastHangTime = self.TimeStateChangeCurrent - self.TimeStateChangePrevious
			else:
				self.LastPauseTime = self.TimeStateChangeCurrent - self.TimeStateChangePrevious

		return self.HangDetected

	def run_measure (self):
		"""
		Start to measure from gyroscope sensor with kalman filter
		"""
		self.init_measurements()

		t = threading.currentThread()

		print ("Start measuring loop")
		timer = time.time()
		flag = 0

		while True:
			if (getattr(t, "do_stop", False)):
				print ("Stop this stuff")
				break

			if(flag >100): #Problem with the connection
				print("There is a problem with the connection")
				flag=0
				continue
			#Read Accelerometer raw value
			accX = self.read_raw_data(self.ACCEL_XOUT_H)
			accY = self.read_raw_data(self.ACCEL_YOUT_H)
			accZ = self.read_raw_data(self.ACCEL_ZOUT_H)

			#Read Gyroscope raw value
			gyroX = self.read_raw_data(self.GYRO_XOUT_H)
			gyroY = self.read_raw_data(self.GYRO_YOUT_H)
			gyroZ = self.read_raw_data(self.GYRO_ZOUT_H)

			dt = time.time() - timer
			timer = time.time()

			if (self.RestrictPitch):
				roll = math.atan2(accY,accZ) * self.radToDeg
				pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * self.radToDeg
			else:
				roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * self.radToDeg
				pitch = math.atan2(-accX,accZ) * self.radToDeg

			gyroXRate = gyroX/131
			gyroYRate = gyroY/131

			if (self.RestrictPitch):

				if((roll < -90 and self.kalAngleX >90) or (roll > 90 and self.kalAngleX < -90)):
					self.kalmanX.setAngle(roll)
					complAngleX = roll
					self.kalAngleX   = roll
					self.gyroXAngle  = roll
				else:
					self.kalAngleX = self.kalmanX.getAngle(roll,gyroXRate,dt)

				if(abs(self.kalAngleX)>90):
					gyroYRate  = -gyroYRate
					self.kalAngleY  = self.kalmanY.getAngle(pitch,gyroYRate,dt)
			else:

				if((pitch < -90 and self.kalAngleY >90) or (pitch > 90 and self.kalAngleY < -90)):
					self.kalmanY.setAngle(pitch)
					compAngleY = pitch
					self.kalAngleY   = pitch
					self.gyroYAngle  = pitch
				else:
					self.kalAngleY = self.kalmanY.getAngle(pitch,gyroYRate,dt)

				if(abs(self.kalAngleY)>90):
					gyroXRate  = -gyroXRate
					self.kalAngleX = self.kalmanX.getAngle(roll,gyroXRate,dt)

			#angle = (rate of change of angle) * change in time
			self.gyroXAngle = gyroXRate * dt
			self.gyroYAngle = self.gyroYAngle * dt

			#compAngle = constant * (old_compAngle + angle_obtained_from_gyro) + constant * angle_obtained from accelerometer
			self.compAngleX = 0.93 * (self.compAngleX + gyroXRate * dt) + 0.07 * roll
			self.compAngleY = 0.93 * (self.compAngleY + gyroYRate * dt) + 0.07 * pitch

			if ((self.gyroXAngle < -180) or (self.gyroXAngle > 180)):
				self.gyroXAngle = self.kalAngleX
			if ((self.gyroYAngle < -180) or (self.gyroYAngle > 180)):
				self.gyroYAngle = self.kalAngleY

			#print("Angle X: " + str(self.kalAngleX)+"   " +"Angle Y: " + str(self.kalAngleY))

			#print(str(roll)+"  "+str(self.gyroXAngle)+"  "+str(self.compAngleX)+"  "+str(kalAngleX)+"  "+str(pitch)+"  "+str(self.gyroYAngle)+"  "+str(self.compAngleY)+"  "+str(kalAngleY))
			#if (kalAngleX < 0):
			#	message = kalAngleX

			self.detect_hang(self.kalAngleX)

			self.create_message()
			time.sleep(self.delay_measures)

	def create_message(self):
		"""
		Assemble the websocket status message.
		"""
		self.message = json.dumps({"AngleX": "{:.2f}".format(self.kalAngleX), "AngleY": "{:.2f}".format(self.kalAngleY),
		"AngleX_NoHang": "{:.2f}".format(self.AngleX_NoHang), "AngleX_Hang": "{:.2f}".format(self.AngleX_Hang),
		"HangDetected": self.HangDetected, "HangStateChanged": self.HangStateChanged,
		"LastHangTime": "{:.2f}".format(self.LastHangTime), "LastPauseTime": "{:.2f}".format(self.LastPauseTime)
		})


	def measure_angle_extremum (self):
		"""
		Routine for measure the extrema -> measure two times ten seconds one shot
		"""
		# FIXME: this can be merged with a continous running measurements loop
		#self.init_measurements()
		
		dt = 0.1
		print ("Measure angle configuration for extremum")

		print ("No hang time")
		tt = 0.0	
		while (tt < self.calibration_duration):
		
			tt = tt + dt
			time.sleep(dt)
			print ("t = %.1f angle = %.1f" %(tt, self.kalAngleX))

		self.AngleX_NoHang = self.kalAngleX

		print ("Time to hang")
		tt = 0.0	
		while (tt < self.calibration_duration):
			tt = tt + dt
			time.sleep(dt)
			print ("t = %.1f angle = %.1f" %(tt, self.kalAngleX))

		self.AngleX_Hang = self.kalAngleX # FIXME: sum of both angles - direction indenpendent?!

		self.create_message()

	def _run_measure_angle_extremum (self):
		"""
		Process to start the thread for calibration.
		"""
		print ("Starting Extremum angle measurement")
		self.run_measure_angle_extremum_thread = threading.Thread(target=self.measure_angle_extremum)
		self.run_measure_angle_extremum_thread.do_stop = False
		self.run_measure_angle_extremum_thread.start()

	def _stop_measure_angle_extremum (self):
		"""
		Process to stop the thread for calibration.
		"""
		print ("Stopping Extremum angle measurement")
		self._run_measure_angle_extremum_thread.do_stop = True

	async def producer_handler(self, websocket, path):
		""" 
		Handler for websocket sending
		"""
		while True:
			#message = await producer()
			if (self.HangStateChanged == True):
				await websocket.send(self.message)
			await asyncio.sleep(self.delay_sending) #new

	async def consumer_handler(self, websocket, path):
		"""
		Handler for websocket receiving
		"""
		async for message in websocket:
			print ("Received it:")
			print (message)
			#await consumer(message)
			if (message == "StartCalibration"):
				self._run_measure_angle_extremum()
			if (message == "StopCalibration"):
				self._stop_measure_angle_extremum()   # TBD to be implemented
			if (message == "StartHangdetection"):
				self._run_start_hangdetection()
			if (message == "StopHangdetection"):
				self._stop_hangdetection()		# TBD to be implemented

	async def handler(self, websocket, path):
		""" 
		Websocket handler - sending and receiving
		"""
		consumer_task = asyncio.ensure_future(
			self.consumer_handler(websocket, path))
		producer_task = asyncio.ensure_future(
			self.producer_handler(websocket, path))

		done, pending = await asyncio.wait(
			[consumer_task, producer_task],
			return_when=asyncio.FIRST_COMPLETED,
		)
		for task in pending:
			task.cancel()
	
	def _run_measure(self):
		"""
		Run continous measurement in a thread
		"""
		print ("Run thread measure")
		self.run_measure_thread = threading.Thread(target=self.run_measure)
		self.run_measure_thread.do_stop = False
		self.run_measure_thread.start()

	def _stop_measure(self):
		"""
		Stopping the measurement thread
		"""
		print ("Stop thread measure")
		self.run_measure_thread.do_stop = True

	def run_handler(self):
		""" 
		Start the websocket handler and wait for commands
		"""
		print ("start handler")
		self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)
		asyncio.get_event_loop().run_until_complete(self.start_server)
		asyncio.get_event_loop().run_forever()




a = Gyroscope()
a.run_handler()