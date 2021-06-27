import time
import paho.mqtt.client as paho
import json
import pandas as pd
import numpy as np
from pymongo import MongoClient

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='MQTT(%(threadName)-10s) %(message)s',
                    )


#numpy_data = np.array([[1, 2], [3, 4]])
#df = pd.DataFrame(data=numpy_data, index=["row1", "row2"], columns=["column1", "column2"])
#print(df)


def on_message(client, userdata, message):
    global df
    msg = json.loads(message.payload.decode("utf-8"))
    #print (msg["time"])
    df = df.append({
     "time": msg["time"],
     "loadcurrent": msg["loadcurrent"],
     "loadaverage": msg["loadaverage"],
     "fti": msg["fti"],
     "rfd": msg["rfd"],
     "loadmaximal": msg["loadmaximal"],
     "loadloss": msg["loadloss"]
    }, ignore_index=True)
    #print (df)
    #print (df["time"].max() )
    #print( df["loadcurrent"].max())
    #write_file()

def write_file():
    compression_opts = dict(method='zip',                         archive_name='out.csv')  
    df.to_csv('out.zip', index=False,          compression=compression_opts)  

df = pd.DataFrame(columns=["time", "loadcurrent", "loadaverage", "fti", "rfd", "loadmaximal", "loadloss" ])
values_to_add ={"time":0, "loadcurrent":0, "loadaverage":0, "fti":0, "rfd":0, "loadmaximal":0, "loadloss":0 }



row_to_add = pd.Series(values_to_add, name='x')
df = df.append(row_to_add)


datenbank = MongoClient('mongodb://localhost:27017/',
 username='root',
  password='example'
  )['hangboard']


nutzerInfo = {
    "name": "Felix Schürmeyer",
  "alter": 22,
  "rolle": "Gründer von HelloCoding.",
  "artikel-anzahl": 40
}
collection = datenbank['test-collection']

collection.insert_one(nutzerInfo)

daten = collection.find_one({"name": "Felix Schürmeyer"})

print(daten) 


client= paho.Client("client-001") 
client.on_message=on_message
client.connect("t20",1883,60)#connect

client.subscribe("hangboard/sensor/load/loadstatus")#subscribe

client.loop_forever()
