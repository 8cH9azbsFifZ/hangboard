import time
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment

import paho.mqtt.client as paho
import json
import time

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Display(%(threadName)-10s) %(message)s',
                    )





class Database():
    def __init__(self):
        # create seven segment device
        self.serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(self.serial, cascaded=1)
        self.seg = sevensegment(self.device)

        # Init timers
        self._time_current = time.time()
        self._time_last = self._time_current 
        self._update_interval = 0.5 # Update interval for display in seconds


    def _on_message(self, client, userdata, message):
        #logging.debug("Write message " + str(message.payload.decode("utf-8")))

        msg = json.loads(message.payload.decode("utf-8"))

        # Check if interval large enough
        time_last = self._time_current 
        self._time_current = time.time()
        del_time = self._time_current - self._time_last
        #logging.debug(del_time)
        if del_time < self._update_interval:
            return
        
        self._time_last = time_last

        print (msg)
        l = "\rLoad: %.1f    " % msg["loadcurrent"]
        t = "Time: " + str(msg["time"])
        lmax = "\rLoad Max: %.1f    " % msg["loadmaximal"]
        ss = l+"\n\r"+lmax
        l2 = msg["loadcurrent_balance"] 
        l1 = msg["loadcurrent"] - l2
        ll = 
        #self._lcd.write_string(ss)
        tt = str("%2.0d  %2.0d"%(l1,l2))
        tt1 = str("%2.0d"%(ll))
        self.seg.text = tt1 #str (msg["loadcurrent"])
        #self._lcd.cursor_pos = (2, 0)


    def _record_data(self, hostname="localhost",port=1883):
        logging.debug("Start recording data from mqtt for display")
        self._client= paho.Client("display_7segment") 
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
    d._record_data(hostname="localhost")        