import time
import paho.mqtt.client as paho
import json
import pandas as pd
import numpy as np
from pymongo import MongoClient

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Database(%(threadName)-10s) %(message)s',
                    )


class Database():
  def __init__(self, hostname="localhost", user="root", password="example"):
    # Init mongo db client
    self._hostname=hostname
    self._port=27017
    self._user=user
    self._password=password
    self._dbname="hangboard"

    self._db = MongoClient('mongodb://'+self._hostname+':'+str(self._port)+'/', username=self._user,   password=self._password  )[self._dbname]

  def _on_message(self, client, userdata, message):
      #global df
      #global coll_raw
      msg = json.loads(message.payload.decode("utf-8"))
      currentData = {"time": msg["time"],
      "loadcurrent": msg["loadcurrent"],
      "loadaverage": msg["loadaverage"],
      "fti": msg["fti"],
      "rfd": msg["rfd"],
      "loadmaximal": msg["loadmaximal"],
      "loadloss": msg["loadloss"]}
      #df = df.append(currentData, ignore_index=True)
      self._coll_raw.insert_one(currentData)
      logging.debug("Write timestamp " + str(msg["time"]))
      #print (df["time"].max() )
      #print( df["loadcurrent"].max())

  def _pd_evals(self):

    df = pd.DataFrame(columns=["time", "loadcurrent", "loadaverage", "fti", "rfd", "loadmaximal", "loadloss" ])
    values_to_add ={"time":0, "loadcurrent":0, "loadaverage":0, "fti":0, "rfd":0, "loadmaximal":0, "loadloss":0 }
    #numpy_data = np.array([[1, 2], [3, 4]])
    #df = pd.DataFrame(data=numpy_data, index=["row1", "row2"], columns=["column1", "column2"])
    #print(df)


    row_to_add = pd.Series(values_to_add, name='x')
    df = df.append(row_to_add)

  def _insert_user(self):

    # Insert a test user
    userInfo = {
      "name": "Karl Klettermax",
      "age": 123,
      "comment": "This is a test user.",
      "uuid": "XYL123"
    }

    collection = self._db['user-collection']
    collection.insert_one(userInfo)

  def _get_user(self):
    # Get information on test user
    collection = self._db['user-collection']
    data = collection.find_one({"name": "Karl Klettermax"}) # FIXME
    uuid = data["uuid"]
    print(uuid) 

  def _set_user(self, uuid):
    self._uuid = uuid
    # Raw collection fo user
    self._coll_raw = self._db[uuid+"-raw"]
    self._coll_summary = self._db[uuid+"-summary"]

  def _set_user_maxload(self, timestamp, hold, load, hangtime, hand):
    userMaxLoadEntry = {
      "time": timestamp,
      "hold": hold,
      "load": load,
      "hangtime": hangtime,
      "hand": hand
    }
    self._coll_summary.insert_one(userMaxLoadEntry)

  def _set_user_bodyweight(self, timestamp, bodyweight):
    userBodyWeight = {
      "time": timestamp,
      "bodyweight": bodyweight
    }
    self._coll_summary.insert_one(userBodyWeight)

  def _get_user_bodyweight(self):
    bw = self._coll_summary.find_one({"bodyweight": {"$gt": 1}}, sort=[("time", -1)]) 
    return bw

  def _get_maxload(self, hold ="JUG", hand = "both"):
    lm = self._coll_summary.find_one({"$and": [{"hold": hold}, {"hand": hand}]}, sort=[("time", -1)])
    return lm


  def _record_data(self, hostname="localhost",port=1883):
    logging.debug("Start recording data from mqtt to database")
    self._client= paho.Client("client-001") 
    self._client.on_message=self._on_message
    self._client.connect(hostname,port,60)#connect

    self._client.subscribe("hangboard/sensor/load/loadstatus")#subscribe

    self._client.loop_forever()
