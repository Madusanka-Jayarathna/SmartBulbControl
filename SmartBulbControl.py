import numpy as np
from pyfirmata import Arduino
import cv2
import os
import math
import HandDetecting

board = Arduino("COM7")                     #connect arduino

# configure pin as PWM output
pin1 = board.get_pin('d:3:p')
pin2 = board.get_pin('d:5:p')
pin3 = board.get_pin('d:9:p')
pin4 = board.get_pin('d:10:p')
pin5 = board.get_pin('d:11:p')

fingerTips = [8,12,16,20]   #finger tips landmarks
overLay = []
sequence_R = []
sequence_L = [0,0,0,0,0]
brightness = 1

imageList = os.listdir("FingerImages")  #images from the source_folder
imageList.sort()                        #sorter out images

for imgNo in imageList:
    image = cv2.imread(f'FingerImages/{imgNo}')
    overLay.append(image)

#open video camera and set the width and height
stream = cv2.VideoCapture(1)
stream.set(3,1280)
stream.set(4,720)

#create object in HandDetector class
detector = HandDetecting.HandDetector()

while True:
    stat, img = stream.read()  # read image from stream
    img = cv2.flip(img,1)
    img,count,label = detector.drawLandmarks(img)
    if count == 2:
        cv2.putText(img, 'Both Hands Detected', (20, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
        cv2.rectangle(img, (760, 10), (1150, 70), (0, 255, 255), cv2.FILLED)
        cv2.putText(img, 'Setting: Brightness', (800, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)

        lmList1,label1 = detector.fingerPosition(img,hand_no=0)
        lmList2, label2 = detector.fingerPosition(img, hand_no=1)
        if label1 == "Right":
            lmList_R = lmList1
            lmList_L = lmList2

        else:
            lmList_R = lmList2
            lmList_L = lmList1

        if lmList_L[20][2] < lmList_L[18][2]:
            x1_R, y1_R = lmList_R[4][1], lmList_R[4][2]
            x1_L, y1_L = lmList_L[4][1], lmList_L[4][2]
            cx, cy = (x1_R + x1_L) // 2, (y1_R + y1_L) // 2
            cv2.circle(img, (x1_R, y1_R), 10, (255, 255, 255), cv2.FILLED)
            cv2.circle(img, (x1_L, y1_L), 10, (255, 255, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)
            cv2.line(img, (x1_R, y1_R), (x1_L, y1_L), (255, 125, 255), 3)

            length = math.hypot(x1_L - x1_R, y1_L - y1_R)
            brightness = np.interp(length, [50, 500], [0, 1])

            brightBar = np.interp(length, [50, 500], [400, 150])
            brightPer = np.interp(length, [50, 500], [0, 100])

            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(img, (50, int(brightBar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(brightPer)}%', (45, 420), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

    else:
        if label == 'Right':
            cv2.putText(img, 'Right Hand', (20, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
            cv2.rectangle(img, (760, 10), (1150, 70), (0, 255, 255), cv2.FILLED)
            cv2.putText(img, 'Setting: Switch OFF', (800, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)

        if label == 'Left':
            cv2.putText(img, 'Left Hand', (460, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
            cv2.rectangle(img, (760, 10), (1150, 70), (0, 255, 255), cv2.FILLED)
            cv2.putText(img, 'Setting: Sequence', (800, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)

            lmList_L,label1 = detector.fingerPosition(img, hand_no=0)
            sequence_L = []
            if len(lmList_L) != 0:
                if lmList_L[4][1] > lmList_L[3][1]:
                    sequence_L.append(1)
                else:
                    sequence_L.append(0)

                for tip in fingerTips:
                    if lmList_L[tip][2] < lmList_L[tip - 2][2]:
                        sequence_L.append(1)
                    else:
                        sequence_L.append(0)
            outSequence = "".join(map(str, sequence_L))
            value = sequence_L.count(1)
            show = int(outSequence, 2)

            img[100:460, 920:1280] = overLay[show]
            cv2.rectangle(img, (920, 100), (1280, 460), (0, 255, 255), 5)

    pin1.write(sequence_L[0] * brightness)
    pin2.write(sequence_L[1] * brightness)
    pin3.write(sequence_L[2] * brightness)
    pin4.write(sequence_L[3] * brightness)
    pin5.write(sequence_L[4] * brightness)

    outSequence1 = " ".join(map(str, sequence_L))
    cv2.rectangle(img, (1035, 665), (1275, 710), (0, 255, 255), cv2.FILLED)
    cv2.putText(img, f"Sequence Set: {outSequence1}", (1050, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (102, 0, 102), 2)
    cv2.putText(img, f"Brightness Set: {int(brightness * 100)}%", (1050, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (102, 0, 102), 2)
    cv2.imshow("LIVE", img)
    cv2.waitKey(1)

