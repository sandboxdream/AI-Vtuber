import threading
import asyncio

class RunThread(threading.Thread):
    def __init__(self, coro):
        self.coro = coro
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.coro)
    
    def close(self):
        # 线程相关清理
        self.join()