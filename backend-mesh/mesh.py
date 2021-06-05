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

async def gyroscope2exercise():
    uri = "ws://localhost:4321"
    uri1 = "ws://10.101.40.81:4323"
    async with websockets.connect(uri) as websocket:
        async with websockets.connect(uri1) as websocket1:
            async for message in websocket1:
                d = json.loads(message)
                if (d["HangStateChanged"] == True):
                    print ("State changed")
                    if (d["HangDetected"] == True):
                        print ("Hang detected")
                        await websocket.send("StartHang")
                    else:
                        print ("No Hang detected")
                        await websocket.send("StopHang")

   

asyncio.get_event_loop().run_until_complete(gyroscope2exercise())
asyncio.get_event_loop().run_forever()