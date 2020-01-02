import cv2 as cv
from threading import Thread
from frame_queue import FrameQueue
import queue


class ImageProvider:
    def __init__(self):
        self.cameras = self.find_cameras()
        self.framesQueue = FrameQueue()

        # Do we have a camera?
        if len(self.cameras) < 1:
           raise UserWarning('No camera device found')

        self.current_camera = self.cameras[0]['index']
        self.cap = cv.VideoCapture(self.current_camera)

        self.framesThread = Thread(target=self.framesThreadBody, daemon=True)
        self.framesThread.start()

    def find_cameras(self, count=1):
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
        try:
            return (True, self.framesQueue.get_nowait())
        except queue.Empty:
            return (False, None)

    def clear_frames(self):
        self.framesQueue.queue.clear()

    def framesThreadBody(self):
        while True:
            hasFrame, frame = self.cap.read()
            if hasFrame:
                frame = cv.flip(frame, 1)
                self.framesQueue.put(frame)

    def get_dimensions(self):
        width = self.cameras[self.current_camera]['width']
        height = self.cameras[self.current_camera]['height']
        return (width, height)
