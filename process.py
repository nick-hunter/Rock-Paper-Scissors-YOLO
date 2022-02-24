import cv2 as cv
import numpy as np
from threading import Thread
from frame_queue import FrameQueue
import queue
import time
import os
import sys
from utils import file_path

class ImageProcessor:
    '''Process images with the OpenCV DNN YOLO implementation.

    Images and predictions are stored in parallel queues.'''
    def __init__(self, ImageProvider, Config):
        self.ImageProvider = ImageProvider
        self.processedQueue = FrameQueue()
        self.predictionQueue = queue.Queue()
        self.processing = False
        self.config = Config
        self.classes = self.load_classes()

        self.processThread = Thread(target=self.processThreadBody, daemon=True)
        self.processThread.start()
        self.draw = False

    def load_classes(self):
        '''Load YOLO model class file'''
        classes_path = self.config.get_property('classes_path')

        if classes_path is None:
            raise KeyError('Configuration property "classes_path" not \
                           configured')

        try:
            f = open(file_path(classes_path), "rt")
            classes = f.read().rstrip('\n').split('\n')
            f.close()
            return classes
        except FileNotFoundError as e:
            print('Class file not found')
            exit(1)

    def get_classes(self):
        '''Returns the ordered list of classes'''
        return self.classes

    def start_processing(self, dt=0):
        '''Start processing images through the neural network'''
        self.processedQueue.queue.clear()
        self.predictionQueue.queue.clear()
        self.processing = True

    def stop_processing(self):
        '''Stop processing images through the neural network'''
        self.processing = False

    def start_drawing(self):
        '''Start drawing circles on processed frames around detected objects'''
        self.draw = True

    def stop_drawing(self):
        '''Stop drawing circles'''
        self.draw = False

    def is_processing(self):
        '''Returns True if images are currently being passed through the network'''
        return self.processing

    def get_frame(self):
        '''Get the next processed frame from the queue

        Returns:
            A tuple where the first item is True if a frame exists in the
            queue. If the frame queue is empty then the first value will be
            False. The second item will either be image data or None depending
            on if an image was availible.
        '''
        try:
            return (True, self.processedQueue.get_nowait())
        except queue.Empty:
            return (False, None)

    def get_frame_predictions(self):
        '''Get YOLO object detections from the prediction queue

        Returns:
            A tuple where the first item is True if a frame prediction exists in the
            queue. The second item is either None (if no predictions are availible),
            or a list of directories. Each dictonary is one object detection and
            contains the following data:
                x: box center pixel along image x-axis,
                y: box center pixel along image y-axis,
                width: box width in pixels,
                height: box height in pixels,
                class: 'Rock', 'Paper', or 'Scissors',
                confidence: Percentage confidence value
        '''
        try:
            return (True, self.predictionQueue.get_nowait())
        except queue.Empty:
            return (False, None)

    def processThreadBody(self):
        '''Thread body which handles YOLO processing'''

        # These values could be updated after the thread starts

        # Get configuration values
        weights_path = file_path(self.config.get_property('weights_path'))
        cfg_path = file_path(self.config.get_property('cfg_path'))

        inpWidth = self.config.get_property('inpWidth')
        inpHeight = self.config.get_property('inpHeight')

        scale = self.config.get_property('scale')
        mean = self.config.get_property('mean')
        confThreshold = self.config.get_property('confThreshold')
        nmsThreshold = self.config.get_property('nmsThreshold')
        circle_scale = self.config.get_property('circle_scale')

        # Iniitialize the OpenCV darknet DNN module
        net = cv.dnn.readNet(weights_path, cfg_path, 'darknet')
        outNames = net.getUnconnectedOutLayersNames()

        frameWidth, frameHeight = self.ImageProvider.get_dimensions()

        while True:
            if not self.processing:
                time.sleep(0.1)
            else:
                ret, frame = self.ImageProvider.get_frame()
                if ret:
                    self.ImageProvider.clear_frames()
                    framePredictions = list()

                    blob = cv.dnn.blobFromImage(frame,
                                                size=(inpWidth, inpHeight),
                                                swapRB=False, ddepth=cv.CV_8U)

                    net.setInput(blob, scalefactor=scale, mean=mean)
                    outs = net.forward(outNames)

                    boxes = []
                    confidences = []
                    classIDs = []

                    for out in outs:
                        for detection in out:
                            scores = detection[5:]
                            classId = np.argmax(scores)
                            confidence = scores[classId]
                            if confidence > confThreshold:
                                center_x = int(detection[0] * frameWidth)
                                center_y = int(detection[1] * frameHeight)
                                width = int(detection[2] * frameWidth)
                                height = int(detection[3] * frameHeight)
                                left = int(center_x - width / 2)
                                top = int(center_y - height / 2)

                                classIDs.append(classId)
                                confidences.append(float(confidence))
                                boxes.append([left, top, width, height])

                    indices = np.arange(0, len(classIDs))

                    for i in indices:
                        box = boxes[i]
                        left = box[0]
                        top = box[1]
                        width = box[2]
                        height = box[3]

                        center_x = int(left+(width/2))
                        center_y = int(top+(height/2))

                        object = self.classes[classIDs[i]]

                        if self.draw:
                            if object == "Rock":
                                color = (255, 0, 0)
                            elif object == "Paper":
                                color = (0, 255, 0)
                            elif object == "Scissors":
                                color = (0, 0, 255)

                            cv.rectangle(frame, (center_x-int(width/2), center_y+int(height/2)), (center_x+int(width/2), center_y-int(height/2)), color)

                        prediction = {
                            'x': center_x,
                            'y': center_y,
                            'width': width,
                            'height': height,
                            'class': object,
                            'confidence': confidences[i]
                        }

                        framePredictions.append(prediction)

                    self.processedQueue.put(frame)
                    self.predictionQueue.put(framePredictions)
