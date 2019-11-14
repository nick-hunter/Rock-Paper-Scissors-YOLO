import cv2 as cv
import numpy as np
from threading import Thread
from frame_queue import frameQueue
import queue

class ImageProcessor:
    def __init__(self, ImageProvider, Config):
        self.ImageProvider = ImageProvider
        self.processedQueue = frameQueue()
        self.predictionQueue = queue.Queue()
        self.processing = True
        self.config = Config
        self.classes = self.load_classes()

        self.processThread = Thread(target=self.processThreadBody, daemon=True)
        self.processThread.start()

    def load_classes(self):
        classes_path = self.config.get_property('classes_path')

        if classes_path == None:
            raise KeyError('Configuration property "classes_path" not configured')

        try:
            f = open(classes_path, "rt")
            classes = f.read().rstrip('\n').split('\n')
            f.close()
            return classes
        except FileNotFoundError as e:
            print('Class file not found')
            exit(1)

    def get_classes(self):
        return self.classes

    def get_frame(self):
        try:
            return (True, self.processedQueue.get_nowait())
        except queue.Empty:
            return (False, None)


    def processThreadBody(self):
        # These values could be updated after the thread starts

        weights_path = self.config.get_property('weights_path')
        cfg_path = self.config.get_property('cfg_path')

        inpWidth = self.config.get_property('inpWidth')
        inpHeight = self.config.get_property('inpHeight')

        scale = self.config.get_property('scale')
        mean = self.config.get_property('mean')
        confThreshold = self.config.get_property('confThreshold')
        nmsThreshold = self.config.get_property('nmsThreshold')
        circle_scale = self.config.get_property('circle_scale')

        net = cv.dnn.readNet(weights_path, cfg_path, 'darknet')
        outNames = net.getUnconnectedOutLayersNames()

        frameWidth, frameHeight = self.ImageProvider.get_dimensions()

        while True:
            if not self.processing:
                ret, frame = ImageProvider.get_frame()
                if ret:
                    processedQueue.put(frame)
            else:
                ret, frame = self.ImageProvider.get_frame()
                if ret:
                    self.ImageProvider.clear_frames()
                    framePredictions = list()

                    blob = cv.dnn.blobFromImage(frame, size=(inpWidth, inpHeight), swapRB=False, ddepth=cv.CV_8U)

                    net.setInput(blob, scalefactor=scale, mean=mean)
                    outs = net.forward(outNames)

                    boxes = []
                    confidences = []
                    classIDs = []

                    for out in outs:
                            for detection in out:
                                scores = detection[5:8]
                                classId = np.argmax(scores)
                                confidence = scores[classId]
                                if confidence > confThreshold:
                                    #object = self.classes[classId]

                                    center_x = int(detection[0] * frameWidth)
                                    center_y = int(detection[1] * frameHeight)
                                    width = int(detection[2] * frameWidth)
                                    height = int(detection[3] * frameHeight)
                                    left = int(center_x - width / 2)
                                    top = int(center_y - height / 2)

                                    classIDs.append(classId)
                                    confidences.append(float(confidence))
                                    boxes.append([left, top, width, height])


                    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
                    for i in indices:
                        i = i[0]
                        box = boxes[i]
                        left = box[0]
                        top = box[1]
                        width = box[2]
                        height = box[3]

                        size = int(((width+height)/2)*circle_scale)
                        center_x = int(left+(width/2))
                        center_y = int(top+(height/2))

                        object = self.classes[classIDs[i]]

                        #cv.rectangle(frame, (center_x-int(width/2), center_y+int(height/2)), (center_x+int(width/2), center_y-int(height/2)), (0, 255, 0))
                        if object == "Rock":
                            color = (255, 0, 0)
                        elif object == "Paper":
                            color = (0, 255, 0)
                        elif object == "Scissors":
                            color = (0, 0, 255)

                        cv.circle(frame, (center_x,center_y), size, color, thickness=3)

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
