import time
from datetime import datetime

import paho.mqtt.client as paho
import json
import time

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Display(%(threadName)-10s) %(message)s',
                    )





class Database():
    def __init__(self):
        return

    def _on_message(self, client, userdata, message):
        #logging.debug("Write message " + str(message.payload.decode("utf-8")))

        msg = json.loads(message.payload.decode("utf-8"))

        hang = msg["HangDetected"] 
        l2 = msg["loadcurrent_balance"] 
        l1 = msg["loadcurrent"] - l2
        ll = msg["loadcurrent"]
        tt = msg["time"]
        if hang == "True":
     
            print (tt,ll,l1,l2)


    def _record_data(self, hostname="localhost",port=1883):
        logging.debug("Start recording data from mqtt for display")
        self._client= paho.Client("text_logger") 
        self._client.on_message=self._on_message
        self._client.connect(hostname,port,60)#connect

        # FIXME: subscribe to all?
        
        self._client.subscribe("hangboard/sensor/load/loadstatus")
        #self._client.subscribe("hangboard/sensor/sensorstatus")
        #self._client.subscribe("hangboard/sensor/lastexercise")
        #self._client.subscribe("hangboard/workout/userstatistics")
        #self._client.subscribe("hangboard/workout/upcoming")

        self._client.loop_forever()


if __name__ == "__main__":
    d = Database()
    d._record_data(hostname="raspi-hangboard")        