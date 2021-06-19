"""
This class handels all mqtt communication

Debug communication using:
mosquitto_sub -h 127.0.0.1 -t hangboard

"""

import paho.mqtt.client as mqtt
import json
import time



import logging
logging.basicConfig(level=logging.DEBUG,
                    format='MQTT(%(threadName)-10s) %(message)s',
                    )



class MQTT_Handler():
    def __init__(self):
        self.dt = 0.1

    def _publisher(self):
        # This is the Publisher

        self._client = mqtt.Client()
        self._client.connect("localhost",1883,60)
        while True:
            tsender = time.time()
            msg = json.dumps({"time_sender": tsender})
            #client.publish("topic/test", time.time()); #"Hello world!");
            self._client.publish("topic/test", msg) #time.time()); #"Hello world!");
            time.sleep(self.dt)
        
        #self._client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self._client.subscribe("topic/test")

    def _on_message(self, client, userdata, msg):
        #if msg.payload.decode() == "Hello world!":
        #msg = float(msg.payload.decode())
        msg = json.loads(msg.payload.decode())
        tloc = time.time()
        delta = msg["time_sender"]-tloc
        print("msg %s loacl %f delta %f " %( msg,tloc,delta)) #time.time())
        #    client.disconnect()
        
    def _subscriber(self):
        # This is the Subscriber

        self._client = mqtt.Client()
        self._client.connect("localhost",1883,60)

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        self._client.loop_forever()


if __name__ == "__main__":
    a = MQTT_Handler()
    a._publisher()