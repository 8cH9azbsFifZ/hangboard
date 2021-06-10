"""
Class for handling all communications from the backend to the frontend.
"""


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Messager(%(threadName)-10s) %(message)s',
                    )


from pydispatch import dispatcher
from aio_pydispatch import Signal
import asyncbg

import time
import asyncio
import threading
import websockets
import os
from aiofile import async_open
from aiofile import AIOFile, LineReader, Writer
import aiofiles

WSHOST = "0.0.0.0" #args.host 
WSPORT = 4321 #args.port 

import janus
from queMorph import *
import redis
from websock import WebSocketServer
import asyncio_redis

"""
Signals for communication
"""
SIGNAL_WORKOUT = 'SignalWorkout'
SIGNAL_MESSAGER = 'SignalMessager'
SIGNAL_EXERCISETIMER = 'SignalExerciseTimer'
SIGNAL_PAUSETIMER = 'SignalPauseTimer'
SIGNAL_ASCIIBOARD = 'AsciiBoard'
SIGNAL_BOARD = 'Board'
SIGNAL_ZLAGBOARD = "SignalZlagboard"

SIGNAL_AIO_MESSAGER = Signal('SignalMessager')
SIGNAL_AIO_WORKOUT = Signal('SignalWorkout')


#class Messager(threading.Thread):
class Messager():
    """
    All stuff for sending the data created in this file using websockets to the frontends.
    """
#    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, dt=0.1):
#        super(Messager,self).__init__()
#        self.target = target
#        self.name = name
    def __init__(self):
        self.daemon = True
        logging.debug ("Init class for messager")
        self.do_stop = False

        self.sampling_interval = 0.1

        self.ws_msg = "Alive"
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.rinput = self.r.pubsub()
        self.rinput.subscribe('workout')



        dispatcher.connect( self.handle_signal, signal=SIGNAL_MESSAGER, sender=dispatcher.Any )
        #SIGNAL_AIO_MESSAGER.connect(self.handle_signal)

        self.read_path = "/tmp/pipe.in"
        if os.path.exists(self.read_path):
            os.remove(self.read_path)
        os.mkfifo(self.read_path)


    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        logging.debug ("Starting thread for messager")

        self.run_websocket_handler()
        #while True:
        #    if (self.do_stop == True):
        #        return
        #    time.sleep(self.sampling_interval)
        #return

    def handle_signal (self, message):
        logging.debug('Messager: Signal detected with ' + str(message) )
        self.ws_msg = str(message)

        #self.my_server.send_all(client, data)

    async def producer_handler(self, websocket, path):
        """
        Send the current status of the exercise every second via websocket.
        """
        while True:
            await websocket.send(self.ws_msg)
            #if "OneMessageOnly" in self.exercise_status:
            #    self.exercise_status = ""
            await asyncio.sleep(self.sampling_interval) 

    async def handler(self, websocket, path):
        """
        Handler for the websockets: Receiving and Sending
        """
        # TODO rework for this version
        consumer_task = asyncio.ensure_future(            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(            self.producer_handler(websocket, path))
        #pipe_task = asyncio.ensure_future(            self.pipe_handler())
        queue_task = asyncio.ensure_future(            self.queue_handler())

        #done, pending = await asyncio.wait(            [consumer_task, producer_task, pipe_task],            return_when=asyncio.FIRST_COMPLETED,
        done, pending = await asyncio.wait(            [consumer_task, producer_task, queue_task],            return_when=asyncio.FIRST_COMPLETED,
        #done, pending = await asyncio.wait(            [consumer_task, producer_task],            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    #async def pipe_handler(self):
        #https://gist.github.com/mightymercado/4efba1f070a6ba6526c3e237f0eb0443 TODO
        #self.rf = os.open(self.read_path, os.O_RDONLY)
    #    while True:
    #        print ("PIPE")

            #async with AIOFile("/tmp/pipe.in", 'r') as afp:
            #    print ("DATEI IST NUN AUF")
            #    async for line in LineReader(afp):
            #        print ("HIER KOMMT ES")
            #        print(line[:-1])
            #sync with async_open("/tmp/pipe.in", 'r+') as afp:
            #    print(await afp.read())
            #async with aiofiles.open('/tmp/pipe.in', mode='r') as f:
            #    async for line in f:
            #        print ("PIPE")
            #        print (line)
    #        await asyncio.sleep(self.sampling_interval) 
        #while True:
        #    print ("PIPE")
        #    await s = os.read(self.rf, 1024)
        #    print (s)
        #    await asyncio.sleep(self.sampling_interval) 


    async def queue_handler(self):
        while True:
            a = self.rinput.get_message()
            #bob_p.get_message()
            # now bob can find alice’s music by simply using get_message()
            #new_music = bob_p.get_message()['data']
            print ("REDIS SHti")
            print(a)
            await asyncio.sleep(self.sampling_interval) 

    async def consumer_handler(self, websocket, path): 
        """
        Handler for receicing commands 
        """
        # TODO rework for this version

        async for message in websocket:
            print ("Received it:")
            print (message)
            await self.consumer(message)


    async def consumer (self, message):
        """
        Execute commands as received from websocket (handler)
        """
        # TODO rework for this version

        print("Received request: %s" % message)
        if (message == "RunSet"):
            SIGNAL_AIO_WORKOUT.send("RunSet") #print ("AHA")
            #dispatcher.send( signal=SIGNAL_WORKOUT, message="RunSet")
        #if (message == "Start"):
        #    self._run_set()
        #if (message == "Stop"):
        #    self._stop_set()     
        #if (message == "GetBoard"):
        #    self.get_board()
        #if (message == "ListWorkouts"): # TBD: Implement in webinterface
        #    self.list_workouts()
        #if (message == "StartHang"):
        #    self.set_start_hang()
        #if (message == "StopHang"):
        #    self.set_stop_hang()

    def run_websocket_handler(self):
        """
        Start the websocket server and wait for input
        """
        logging.debug ("Start websocket handler")

        self.start_server = websockets.serve(self.handler, WSHOST, WSPORT)

        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()
    
    @asyncio.coroutine
    def example(self):
        # Create connection
        connection = yield from asyncio_redis.Connection.create(host='127.0.0.1', port=6379)

        # Create subscriber.
        subscriber = yield from connection.start_subscribe()

        # Subscribe to channel.
        yield from subscriber.subscribe([ 'workout' ])

        # Inside a while loop, wait for incoming events.
        while True:
            reply = yield from subscriber.next_published()
            print('Received: ', repr(reply.value), 'on channel', reply.channel)

        # When finished, close the connection.
        connection.close()



    def start_other_server(self):
        self.my_server = WebSocketServer(
            "0.0.0.0",        # Example host.
            4321,               # Example port.
            on_data_receive     = self.on_data_receive,
            on_connection_open  = self.on_connection_open,
            on_error            = self.on_error,
            on_connection_close = self.on_connection_close,
            on_server_destruct  = self.on_server_destruct
        )
        self.my_server.serve_forever()


    def on_data_receive(self, client, data):
        '''Called by the WebSocket server when data is received.'''
        # Your implementation here.
        if (data == "RunSet"):
            SIGNAL_AIO_WORKOUT.send("RunSet") #print ("AHA")
            #dispatcher.send( signal=SIGNAL_WORKOUT, message="RunSet")

    def on_connection_open(self, client):
        '''Called by the WebSocket server when a new connection is opened.'''
        # Your implementation here.
        print("REC")

    def on_error(self, exception):
        '''Called by the WebSocket server whenever an Exception is thrown.'''
        # Your implementation here.
        print("REC")
 
    def on_connection_close(self, client):
        '''Called by the WebSocket server when a connection is closed.'''
        # Your implementation here.
        print("REC")

    def on_server_destruct(self):
        '''Called immediately prior to the WebSocket server shutting down.'''
        # Your implementation here.
        print("REC")
