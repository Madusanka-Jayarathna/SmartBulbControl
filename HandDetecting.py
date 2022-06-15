import cv2
import mediapipe as mp
import math
from google.protobuf.json_format import MessageToDict

#create a class to detect hand
class HandDetector():
    def __init__(self, static_image_mode=False, max_num_hands=2, model_complexity=1,
                 min_detection_confidence=0.5,min_tracking_confidence=0.5):                                             #parameters of the class
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.hands = mp.solutions.hands                                                                                 #apply to mediapipe
        self.hand = self.hands.Hands(self.static_image_mode,self.max_num_hands,
                                     self.model_complexity,self.min_detection_confidence,self.min_tracking_confidence)
        self.handDraw = mp.solutions.drawing_utils


    #drawing landmarks of the hands and return the marked image
    def drawLandmarks(self,img,draw=True):
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.results = self.hand.process(imgRGB)
        label = "No Hands"
        count = 0

        if self.results.multi_hand_landmarks:
            count = len(self.results.multi_handedness)
            for i in self.results.multi_handedness:
                label = MessageToDict(i)['classification'][0]['label']
            for lmks in self.results.multi_hand_landmarks:
                if draw:
                    self.handDraw.draw_landmarks(img, lmks, self.hands.HAND_CONNECTIONS,
                                        self.handDraw.DrawingSpec(color=(102, 0, 102), thickness=3, circle_radius=3),
                                        self.handDraw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2))

        return img,count,label


    #get the details of each land mark and draw bounding box then return the details
    def fingerPosition(self,img, hand_no=0, box=False):
        self.lmList = []
        xList = []
        yList = []
        bbox = []
        label = "No Hands"
        if self.results.multi_hand_landmarks:
            for i in self.results.multi_handedness:
                label = MessageToDict(i)['classification'][0]['label']
            myHand = self.results.multi_hand_landmarks[hand_no]
            for no, lmk in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lmk.x * w), int(lmk.y * h)
                self.lmList.append([no, cx, cy])
                xList.append(cx)
                yList.append(cy)

                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                bbox = [xmin,ymin,xmax,ymax]

                if box:
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20), (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
        return self.lmList,label


    #get the distance of specified two landmarks and draw the connnection line then return distance inbetween and position matrix
    def fingerDistance(self,img,p1,p2,draw=True):
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        if draw:
            cv2.circle(img, (x1, y1), 10, (255, 255, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 255, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 125, 255), 3)

        length = math.hypot(x2 - x1, y2 - y1)
        return length,[x1,y1,x2,y2,cx,cy]



