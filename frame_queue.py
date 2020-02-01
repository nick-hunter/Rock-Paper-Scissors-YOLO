import time
import queue


class FrameQueue(queue.Queue):
    '''Inherited queue data type with framerate calculation support.'''
    def __init__(self):
        queue.Queue.__init__(self, maxsize=10)
        self.startTime = 0
        self.frameCount = 0

    def put(self, frame):
        '''Put an image in the queue

        Args:
            frame: OpenCV image object
        '''
        if(self.startTime == 0):
            self.startTime = time.time()

        queue.Queue.put(self, frame)
        self.frameCount += 1

    def fps(self):
        '''Get queue frames per second.'''
        return self.frameCount // (time.time() - self.startTime)
