"""
This file handles the led progress bar on a moonboard.
18 Rows, K Columns
=> F is the middle one

# cf: https://github.com/8cH9azbsFifZ/moonboard/blob/master/led/moonboard.py
"""

# TODO: Implementation and make compatible with moonboard 

import paho.mqtt.client as mqtt
import logging
logging.basicConfig(level=logging.DEBUG, format='Workout(%(threadName)-10s) %(message)s',)
import json

class ProgressMoonboard():
    def __init__(self, hostname="hangboard", port=1883):

        self._client = mqtt.Client()

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(hostname, port,60)

    def _on_connect(self, client, userdata, flags, rc):
        """ Connect to MQTT broker and subscribe to control messages """
        print("Connected with result code "+str(rc))
        self._client.subscribe("hangboard/workout/timerstatus")

    def _on_message(self, client, userdata, msg):
        """ 
        Receive MQTT control messages.
        Start with debugging on commandline using:
        mosquitto_sub -h localhost -t hangboard/workout/timerstatus
        """
        logging.debug(">MQTT: " + msg.payload.decode())
        self._raw_data = msg.payload.decode()
        self._data = json.loads(self._raw_data)   
        self._completed = self._data["Completed"]
        self._timer_completed()

    def _timer_completed(self):
        #                self.layout.set(self.MAPPING[hold], color)
        #                           color = COLORS.green             
        led_active = []
        for i in range(1,int(self._completed*10+1)):
            led_active.append("F"+str(i))
        print (led_active)
        # FIXME: complete this
    
    def _core_loop(self):
        samplingrate = 0.01

        while True:
            self._client.loop(samplingrate) #blocks for 100ms (or whatever variable given, default 1s)


if __name__ == "__main__":
    l = ProgressMoonboard()
    l._core_loop()
