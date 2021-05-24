import asyncio
import zmq
import zmq.asyncio


HOST = '127.0.0.1'
PORT = 9090
TASK_SOCKET = zmq.asyncio.Context().socket(zmq.SUB)
TASK_SOCKET.connect('tcp://{}:{}'.format(HOST, PORT))



async def recv_and_process():
    
    msg = await TASK_SOCKET.recv_json() 
    reply = await async_process(msg)
    print (msg)


print ("start")
asyncio.run(recv_and_process())
print ("ok")
