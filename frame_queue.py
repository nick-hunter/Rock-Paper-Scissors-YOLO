import time
import queue

class frameQueue(queue.Queue):
    def __init__(self):
        queue.Queue.__init__(self, maxsize=10)
        self.startTime = 0
        self.frameCount = 0

    def put(self, frame):
        if(self.startTime == 0):
            self.startTime = time.time()

        queue.Queue.put(self, frame)
        self.frameCount += 1

    def fps(self):
        return self.frameCount // (time.time() - self.startTime)
