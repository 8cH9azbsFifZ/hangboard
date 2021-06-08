"""
Gyroscope sensor using a kalman filter.
"""

from io import TextIOBase
from Kalman import KalmanAngle
import time
import math

import json

from threading import Thread
import threading

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Gyroscope(%(threadName)-10s) %(message)s',
                    )

import smbus			#import SMBus module of I2C

class Gyroscope(threading.Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

		super(Gyroscope, self).__init__()
		logging.debug('Init Gyroscope Class')
		#Initialize gyroscope class with the neccessary variables for the SMBus module (I2C).
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
		self.init_measurements()

		self.flag = 0


	def init_gyro(self):
		#Initialize GPIO BUS
		logging.debug('Init GPIO Bus')
		self.bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
		self.DeviceAddress = 0x68   # MPU6050 device address

		self.MPU_Init()

		time.sleep(1)

	def MPU_Init(self):
		#Read the gyro and acceleromater values from MPU6050.
		logging.debug('Init MPU')

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
		#Reading raw data from gyroscope
		logging.debug('Read raw data')

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
		#Initialize measurements.
		logging.debug('Set initial parameters')

		self.kalmanX = KalmanAngle()
		self.kalmanY = KalmanAngle()

		logging.debug('Read startup parameters')
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
		logging.debug(roll)

		self.kalmanX.setAngle(roll)
		self.kalmanY.setAngle(pitch)
		self.gyroXAngle = roll;
		self.gyroYAngle = pitch;
		self.compAngleX = roll;
		self.compAngleY = pitch;


	def run_measure (self):
		#Start to measure from gyroscope sensor with kalman filter
		timer = time.time()

		while True:
			self.run_one_measure(self)
	
	def run_one_measure(self):
		if(self.flag >100): #Problem with the connection
			logging.debug("There is a problem with the connection")
			self.flag=0
			#continue

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
		
		logging.debug(str(roll)+"  "+str(self.gyroXAngle)+"  "+str(self.compAngleX)+"  "+str(kalAngleX)+"  "+str(pitch)+"  "+str(self.gyroYAngle)+"  "+str(self.compAngleY)+"  "+str(kalAngleY))

		#print()
		#if (kalAngleX < 0):
		#	message = kalAngleX

		#self.detect_hang(self.kalAngleX)

		#self.create_message()
		#time.sleep(self.delay_measures)

if __name__ == "__main__":
	a = Gyroscope()
	#a.run_handler()