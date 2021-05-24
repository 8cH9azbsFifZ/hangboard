import zmq

import time
import json

from threading import Thread

HOST = '127.0.0.1'
PORT = 9090


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://{}:{}'.format(HOST, PORT))

socket.send_json(json.dumps({"Type": "ok"}))
