import zmq


HOST = '127.0.0.1'
PORT = 9090
TASK_SOCKET = zmq.Context().socket(zmq.SUB)
TASK_SOCKET.connect('tcp://{}:{}'.format(HOST, PORT))

# Subscribes to all topics
TASK_SOCKET.subscribe("")

# Receives a string format message
while 1:
    #a = TASK_SOCKET.recv_string()
    a = TASK_SOCKET.recv_json()

    print (a)