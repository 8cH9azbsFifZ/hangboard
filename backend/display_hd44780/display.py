from RPLCD.i2c import CharLCD
import paho.mqtt.client as paho


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Display(%(threadName)-10s) %(message)s',
                    )





class Database():
    def __init__(self):

        self.lcd = CharLCD('PCF8574', 0x27, backlight_enabled=True, charmap='A02')


    def _on_message(self, client, userdata, message):
        logging.debug("Write message " + str(message.payload.decode("utf-8")))

        msg = json.loads(message.payload.decode("utf-8"))
        
        self._coll_raw.insert_one(msg)


    def _record_data(self, hostname="localhost",port=1883):
        logging.debug("Start recording data from mqtt to database")
        self._client= paho.Client("client-001")  # FIXME
        self._client.on_message=self._on_message
        self._client.connect(hostname,port,60)#connect

        # FIXME: subscribe to all?
        self._client.subscribe("hangboard/workout/holds")
        self._client.subscribe("hangboard/workout/workoutlist")
        self._client.subscribe("hangboard/workout/setinfo")
        self._client.subscribe("hangboard/workout/timerstatus")
        self._client.subscribe("hangboard/workout/status")
        self._client.subscribe("hangboard/workout/workoutstatus")
        self._client.subscribe("hangboard/sensor/load/loadstatus")
        self._client.subscribe("hangboard/sensor/sensorstatus")
        self._client.subscribe("hangboard/sensor/lastexercise")
        self._client.subscribe("hangboard/workout/userstatistics")
        self._client.subscribe("hangboard/workout/upcoming")

        self._client.loop_forever()


if __name__ == "__main__":
    d = Database(hostname="raspi-hangboard", user="root", password="rootpassword")
    d._record_data(hostname="raspi-hangboard")        