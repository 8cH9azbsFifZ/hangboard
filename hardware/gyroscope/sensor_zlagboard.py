# use kalman filter module

# initialize / calibrate

# measure state
# connect to websocket of exercise timer
# send start / stop events to exercise timer




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

WSHOST = "10.101.40.40" # args.host  # FIXME
WSPORT = 4321 #args.port 

message = "start"

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
			

kalmanX = KalmanAngle()
kalmanY = KalmanAngle()

RestrictPitch = True	#Comment out to restrict roll to +-90deg instead - please read: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf
radToDeg = 57.2957786
kalAngleX = 0
kalAngleY = 0
#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


#Read the gyro and acceleromater values from MPU6050
def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(DeviceAddress, SMPLRT_DIV, 7)

	#Write to power management register
	bus.write_byte_data(DeviceAddress, PWR_MGMT_1, 1)

	#Write to Configuration register
	#Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
	bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))

	#Write to Gyro configuration register
	bus.write_byte_data(DeviceAddress, GYRO_CONFIG, 24)

	#Write to interrupt enable register
	bus.write_byte_data(DeviceAddress, INT_ENABLE, 1)


def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(DeviceAddress, addr)
        low = bus.read_byte_data(DeviceAddress, addr+1)

        #concatenate higher and lower value
        value = ((high << 8) | low)

        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value



def measure_loop ():
	print ("Read startup parameters")
	
	#Read Accelerometer raw value
	accX = read_raw_data(ACCEL_XOUT_H)
	accY = read_raw_data(ACCEL_YOUT_H)
	accZ = read_raw_data(ACCEL_ZOUT_H)

	#print(accX,accY,accZ)
	#print(math.sqrt((accY**2)+(accZ**2)))
	if (RestrictPitch):
		roll = math.atan2(accY,accZ) * radToDeg
		pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * radToDeg
	else:
		roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * radToDeg
		pitch = math.atan2(-accX,accZ) * radToDeg
	print(roll)
	kalmanX.setAngle(roll)
	kalmanY.setAngle(pitch)
	gyroXAngle = roll;
	gyroYAngle = pitch;
	compAngleX = roll;
	compAngleY = pitch;

	print ("Start measuring loop")
	timer = time.time()
	flag = 0

	while True:
		if(flag >100): #Problem with the connection
			print("There is a problem with the connection")
			flag=0
			continue
		#Read Accelerometer raw value
		accX = read_raw_data(ACCEL_XOUT_H)
		accY = read_raw_data(ACCEL_YOUT_H)
		accZ = read_raw_data(ACCEL_ZOUT_H)

		#Read Gyroscope raw value
		gyroX = read_raw_data(GYRO_XOUT_H)
		gyroY = read_raw_data(GYRO_YOUT_H)
		gyroZ = read_raw_data(GYRO_ZOUT_H)

		dt = time.time() - timer
		timer = time.time()

		if (RestrictPitch):
			roll = math.atan2(accY,accZ) * radToDeg
			pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * radToDeg
		else:
			roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * radToDeg
			pitch = math.atan2(-accX,accZ) * radToDeg

		gyroXRate = gyroX/131
		gyroYRate = gyroY/131

		if (RestrictPitch):

			if((roll < -90 and kalAngleX >90) or (roll > 90 and kalAngleX < -90)):
				kalmanX.setAngle(roll)
				complAngleX = roll
				kalAngleX   = roll
				gyroXAngle  = roll
			else:
				kalAngleX = kalmanX.getAngle(roll,gyroXRate,dt)

			if(abs(kalAngleX)>90):
				gyroYRate  = -gyroYRate
				kalAngleY  = kalmanY.getAngle(pitch,gyroYRate,dt)
		else:

			if((pitch < -90 and kalAngleY >90) or (pitch > 90 and kalAngleY < -90)):
				kalmanY.setAngle(pitch)
				complAngleY = pitch
				kalAngleY   = pitch
				gyroYAngle  = pitch
			else:
				kalAngleY = kalmanY.getAngle(pitch,gyroYRate,dt)

			if(abs(kalAngleY)>90):
				gyroXRate  = -gyroXRate
				kalAngleX = kalmanX.getAngle(roll,gyroXRate,dt)

		#angle = (rate of change of angle) * change in time
		gyroXAngle = gyroXRate * dt
		gyroYAngle = gyroYAngle * dt

		#compAngle = constant * (old_compAngle + angle_obtained_from_gyro) + constant * angle_obtained from accelerometer
		compAngleX = 0.93 * (compAngleX + gyroXRate * dt) + 0.07 * roll
		compAngleY = 0.93 * (compAngleY + gyroYRate * dt) + 0.07 * pitch

		if ((gyroXAngle < -180) or (gyroXAngle > 180)):
			gyroXAngle = kalAngleX
		if ((gyroYAngle < -180) or (gyroYAngle > 180)):
			gyroYAngle = kalAngleY

		print("Angle X: " + str(kalAngleX)+"   " +"Angle Y: " + str(kalAngleY))
		#print(str(roll)+"  "+str(gyroXAngle)+"  "+str(compAngleX)+"  "+str(kalAngleX)+"  "+str(pitch)+"  "+str(gyroYAngle)+"  "+str(compAngleY)+"  "+str(kalAngleY))
		if (kalAngleX < 0):
			message = 1234; #ws.send("1234")
		time.sleep(0.005)


async def producer_handler(websocket, path):
	while True:
		#message = await producer()
		message ="test"
		await websocket.send(message)
		await asyncio.sleep(1) #new

async def consumer_handler(websocket, path):
	async for message in websocket:
		print ("Received it:")
		print (message)
		#await consumer(message)
		measure_loop()

async def handler(websocket, path):
	consumer_task = asyncio.ensure_future(
		consumer_handler(websocket, path))
	producer_task = asyncio.ensure_future(
		producer_handler(websocket, path))

	done, pending = await asyncio.wait(
		[consumer_task, producer_task],
		return_when=asyncio.FIRST_COMPLETED,
	)
	for task in pending:
		task.cancel()

def run_handler():
	print ("start handler")
	start_server = websockets.serve(handler, WSHOST, WSPORT)
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()

print ("Initialize BUS")
bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
DeviceAddress = 0x68   # MPU6050 device address

MPU_Init()

time.sleep(1)







run_handler()