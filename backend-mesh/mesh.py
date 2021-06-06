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


"""
TO be fixed:
websockets.exceptions.ConnectionClosedError: code = 1006 (connection closed abnormally [internal]), no reason
...
All pieces marked with "# Workaround 1006" contain a part of the proposed solutions
cf. https://stackoverflow.com/questions/54101923/1006-connection-closed-abnormally-error-with-python-3-7-websockets

"""

async def gyroscope2exercise():
    """
    If a hang is detected with the gyroscope sensor it shall send an event to 
    the exercise timer.
    """
    print ("Link gyroscope hang detection to exercise timer")
    async with websockets.connect(WS_EXERCISE, ping_interval=None) as ws_exercise: # Workaround 1006
        async with websockets.connect(WS_GYROSCOPE, ping_interval=None) as ws_gyroscope: # Workaround 1006
            async for message in ws_gyroscope:
                d = json.loads(message)
                print (d)
                if (d["HangStateChanged"] == True):
                    print ("State changed")
                    if (d["HangDetected"] == True):
                        print ("Hang detected")
                        try: # Workaround 1006
                            await ws_exercise.send("StartHang")
                        except asyncio.TimeoutError: # Workaround 1006
                            print("Time's up!")
                    else:
                        print ("No Hang detected")
                        try: # Workaround 1006
                            await ws_exercise.send("StopHang")   
                        except asyncio.TimeoutError: # Workaround 1006
                            print("Time's up!")   
                await ws_gyroscope.recv() # Workaround 1006
                await ws_exercise.recv() # Workaround 1006

            await ws_exercise.recv() # Workaround 1006
            await ws_gyroscope.recv() # Workaround 1006


asyncio.get_event_loop().run_until_complete(gyroscope2exercise())
asyncio.get_event_loop().run_forever()

