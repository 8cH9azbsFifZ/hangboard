"""
Backend mesh:
Integration of the hangboard sensors with the exercise timer.
This logic should not be implemented in the frontend...
"""


import time
import json
import argparse
import os


import asyncio
import websockets

# Parse commandline
parser = argparse.ArgumentParser(description="Mesh Backend.")
parser.add_argument ('--socket_exercise')
parser.add_argument ('--socket_gyroscope')
args = parser.parse_args()

WS_EXERCISE = args.socket_exercise 
WS_GYROSCOPE = args.socket_gyroscope 


async def gyroscope2exercise():
    """
    If a hang is detected with the gyroscope sensor it shall send an event to 
    the exercise timer.
    """
    print ("Link gyroscope hang detection to exercise timer")
    async with websockets.connect(WS_EXERCISE) as ws_exercise:
        async with websockets.connect(WS_GYROSCOPE) as ws_gyroscope:
            async for message in ws_gyroscope:
                d = json.loads(message)
                if (d["HangStateChanged"] == True):
                    print ("State changed")
                    if (d["HangDetected"] == True):
                        print ("Hang detected")
                        await ws_exercise.send("StartHang")
                    else:
                        print ("No Hang detected")
                        await ws_exercise.send("StopHang")   

asyncio.get_event_loop().run_until_complete(gyroscope2exercise())
asyncio.get_event_loop().run_forever()