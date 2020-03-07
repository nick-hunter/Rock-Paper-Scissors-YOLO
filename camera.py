import cv2 as cv
from threading import Thread
from frame_queue import FrameQueue
import queue


class ImageProvider:
    '''The ImageProvider class handles all camera interactions.
    Images are stored in a FrameQueue.'''
    def __init__(self):
        self.cameras = self.find_cameras()
        self.framesQueue = FrameQueue()

        # Do we have a camera?
        if len(self.cameras) < 1:
           raise UserWarning('No camera device found')

        self.current_camera = self.cameras[0]['index']
        self.cap = cv.VideoCapture(self.current_camera)

        self.framesThread = Thread(target=self.frames_thread_body, daemon=True)
        self.framesThread.start()

    def find_cameras(self, count=1):
        '''Enumerate through a number of cameras.

        Args:
            count: The number of cameras to search for. OpenCV does not
            currently support a better way of finding all connected cameras.

        Returns:
            A list with each camera represented by a dictionary. Index value is
            the OpenCV camera index. Width and height are the frame width and
            height in pixels.
        '''
        cameras = list()
        for i in range(count):
            try:
                cap = cv.VideoCapture(i)
                if cap is not None and cap.isOpened():
                    cameras.append({
                        'index': i,
                        'width': cap.get(cv.CAP_PROP_FRAME_WIDTH),
                        'height': cap.get(cv.CAP_PROP_FRAME_HEIGHT)
                    })
            except Exception as e:
                pass
        return cameras

    def get_frame(self):
        '''Get the next frame from the queue

        Returns:
            A tuple where the first item is True if a frame exists in the
            queue. If the frame queue is empty then the first value will be
            False. The second item will either be image data or None depending
            on if an image was availible.
        '''
        try:
            return (True, self.framesQueue.get_nowait())
        except queue.Empty:
            return (False, None)

    def clear_frames(self):
        '''Clear out the frames queue'''
        self.framesQueue.queue.clear()

    def frames_thread_body(self):
        '''Daemon thread to capture images and place them in the frames queue'''
        while True:
            hasFrame, frame = self.cap.read()
            if hasFrame:
                frame = cv.flip(frame, 1)
                self.framesQueue.put(frame)

    def get_dimensions(self):
        '''Return a tuple (width, height) with current camera frame dimensions'''
        width = self.cameras[self.current_camera]['width']
        height = self.cameras[self.current_camera]['height']
        return (width, height)
