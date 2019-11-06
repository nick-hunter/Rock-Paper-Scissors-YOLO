import cv2 as cv
import numpy as np
import sys
import time
import os
import random
import queue
from threading import Thread

rps = ['Rock', 'Paper', 'Scissors']
user_score = 0
computer_score = 0

classes_path = 'model/obj.names'
cfg_path = 'model/yolov3-three.cfg'
weights_path = 'model/yolov3-rps_final.weights'

inpWidth = 416
inpHeight = 416

scale = 0.00392
mean = [0,0,0]
confThreshold = 0.45
nmsThreshold = 0.01
circle_scale = 0.65

frames = 0

# Load class names
classes = None
try:
    f = open(classes_path, "rt")
    classes = f.read().rstrip('\n').split('\n')
    f.close()
except FileNotFoundError as e:
    print('Class file not found')
    exit(1)

net = cv.dnn.readNet(weights_path, cfg_path, 'darknet')
outNames = net.getUnconnectedOutLayersNames()


class frameQueue(queue.Queue):
    def __init__(self):
        queue.Queue.__init__(self)
        self.startTime = 0
        self.frameCount = 0

    def put(self, frame):
        if(self.startTime == 0):
            self.startTime = time.time()

        queue.Queue.put(self, frame)
        self.frameCount += 1

    def fps(self):
        return self.frameCount // (time.time() - self.startTime)


cap = cv.VideoCapture(0)


framesQueue = frameQueue()
processedQueue = frameQueue()
predictionQueue = queue.Queue()
process = True


def framesThreadBody():
    global framesQueue, process

    while process:
        hasFrame, frame = cap.read()
        if hasFrame:
            framesQueue.put(frame)


def processThreadBody():
    global processedQueue, computer_score, user_score
    frame = None

    while process:
        # Get a frame
        try:
            object = None

            frame = framesQueue.get_nowait()
            frameHeight = frame.shape[0]
            frameWidth = frame.shape[1]

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
                            user_choice = classes[classId]

                            object = user_choice

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

                user_choice = classes[classIDs[i]]
                #print(user_choice + ' - ' + str(confidences[i]))

                #cv.rectangle(frame, (center_x-int(width/2), center_y+int(height/2)), (center_x+int(width/2), center_y-int(height/2)), (0, 255, 0))
                if user_choice == "Rock":
                    color = (255, 0, 0)
                elif user_choice == "Paper":
                    color = (0, 255, 0)
                elif user_choice == "Scissors":
                    color = (0, 0, 255)

                cv.circle(frame, (center_x,center_y), size, color, thickness=3)

                prediction = {
                    'x': center_x,
                    'y': center_y,
                    'width': width,
                    'height': height,
                    'class': user_choice,
                    'confidence': confidences[i]
                }

                predictionQueue.put(prediction)

                # Object class
                #label = 'Object: %s' % (object)
                #cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            # Score
            label = 'Computer: %i, Player: %i' % (computer_score, user_score)
            cv.putText(frame, label, (0, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))

            processedQueue.put(frame)
            framesQueue.queue.clear()
            #predictionQueue.queue.clear()


        except queue.Empty:
            pass


def gameplayThreadBody():
    global user_score, computer_score
    print('hey')


framesThread = Thread(target=framesThreadBody)
framesThread.start()

processThread = Thread(target=processThreadBody)
processThread.start()

while cv.waitKey(1) < 0:
    try:
        frame = processedQueue.get_nowait()
        cv.imshow('test', frame)
        print(predictionQueue.get_nowait())

        #print('FPS: ' + str(processedQueue.fps()))
    except queue.Empty:
        pass

process = False
framesThread.join()
processThread.join()

exit(0)

while(user_score < 3 and computer_score < 3):
    print("Rock...")
    time.sleep(1)
    print("Paper...")
    time.sleep(1)
    print("Scissors...")
    time.sleep(1)
    print("Shoot")


    computer_choice = random.choice(rps)
    user_choice = None

    while(user_choice == None):

        #retval, frame = cap.read()

        if(retval):
            frame = cv.resize(frame, (inpWidth, inpHeight))
            #blur = cv.Laplacian(frame, cv.CV_64F).var()
            #print(blur)
            frameHeight = frame.shape[0]
            frameWidth = frame.shape[1]

            blob = cv.dnn.blobFromImage(frame, size=(frameWidth, frameHeight), swapRB=False, ddepth=cv.CV_8U)

            net.setInput(blob, scalefactor=scale, mean=mean)
            outs = net.forward(outNames)
            frames += 1
            end = time.time()

            for out in outs:
                    for detection in out:
                        scores = detection[5:8]
                        classId = np.argmax(scores)
                        confidence = scores[classId]
                        if confidence > confThreshold:
                            print(classes[classId] + ' - ' + str(confidence))
                            user_choice = classes[classId]


        cv.imshow('Rock Paper Scissors',frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    print("Computer chose " + computer_choice)
    print("You chose " + user_choice)
    print("\n")

    if(computer_choice == user_choice):
        print("Tie game! \n")
    elif(user_choice == "Rock"):
        if computer_choice == "Paper":
            computer_score += 1
            print("Computer wins! \n")
        else:
            user_score += 1
            print("You won! \n")
    elif(user_choice == "Paper"):
        if computer_choice == "Scissors":
            computer_score += 1
            print("Computer wins! \n")
        else:
            user_score += 1
            print("You won! \n")
    elif(user_choice == "Scissors"):
        if computer_choice == "Rock":
            computer_score += 1
            print("Computer wins! \n")
        else:
            user_score += 1
            print("You won! \n")

print("Final Score:")
print(str(computer_score) + " computer")
print(str(user_score) + " you")

# When everything is done release the capture
cap.release()
cv.destroyAllWindows()
