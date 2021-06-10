import queue
import asyncio

class queMorph(queue.Queue):
    def __init__(self,qSize,qNM):
        super().__init__(qSize)
        self.timeout=0.018
        self.me=f'queMorph-{qNM}'
    #Introduce methods for async awaitables morph of Q
    async def aget(self):
        while True:
            try:
                return self.get_nowait()
            except queue.Empty:
                await asyncio.sleep(self.timeout)
            except Exception as E:
                raise
    async def aput(self,data):
        while True:
            try:
                return self.put_nowait(data)
            except queue.Full:
                print(f'{self.me} Queue full on put..')
                await asyncio.sleep(self.timeout)
            except Exception as E:
                raise


qqq = queMorph(10,1234)