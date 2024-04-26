import cv2
import mediapipe as mp
import time
import sys

from src.exception import CustomException
from src.logger import logging

#Create a class for hand detection
class handDetector():
    '''
        This is the main class for detecting the hand, 
        detecting the landmarks,drawing the hand land marks,
        find the position of the hand landmarks.
    '''
    def __init__(self,mode = False,maxHands = 1,modelComplex = 1,detectionCon = 0.5,trackCon= 0.5):
        '''
            Initialize the Hand Detector with required parameters.


            Parameters:
                1. mode -> tells the mode of detection
                2. maxHands -> no. of allowed hands for detection
                3. modelComplex -> complexity of the model
                4. detectionCon -> detection confidence threshold, It determines the minimum confidence 
                    level required for a hand detection to be considered valid. 
                    Lower confidence detections are likely discarded.
                5.  trackCon ->  tracking confidence threshold. It determines the minimum confidence 
                    level required for the tracker to continue tracking a detected hand across 
                    consecutive frames. Lower confidence tracking might result in the tracker 
                    losing track of the hand.
                6. mpHands -> Mediapipe hands
        '''
        logging.info("Initializing Hand Detection class")
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplex
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        #Store the retuns of mediapipe functions - solutions, hands, Hands
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands,self.modelComplex,self.detectionCon,self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        logging.info("Initialized hand detection class")

    #Create a method to finds the hands
    def findHands(self,img, draw = True):
        '''
            finds the hands and draws hand landmarks accordingly

            Parameters:
                img -> input image
        '''

        try:
            logging.info("Detecting the input image")
            #Detect the image
            imgRBG = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

            logging.info("Processing the image, detecting the hands")
            #Process the image
            self.results = self.hands.process(imgRBG)
            
            #detect the hand landmarks, 
            if self.results.multi_hand_landmarks:
                #If multiple landmarks, then run a loop over them
                for handlms in self.results.multi_hand_landmarks:
                    if draw:
                        logging.info("Drawing the landmarks, if available")
                        #Draw the hand land marks
                        self.mpDraw.draw_landmarks(img,handlms,self.mpHands.HAND_CONNECTIONS)

            return img
        
        except Exception as e:
            logging.info("Error occured while finding the hands")
            raise CustomException(e,sys)


    
    #create a method to find the position and distance of the detected hand landmarks
    def findPosition(self,img,handNo=0,draw = True):
        '''
            Finds the actual positions of the hand landmarks
            Stores the x, y position and id of the finger
        '''
        try:
            #Define a list to save the co ordinates
            logging.info("Defining the list to store the co ordinates of the hand landmarks")
            lmlist = []
            if self.results.multi_hand_landmarks:
                myHand = self.results.multi_hand_landmarks[handNo]


                for id,lm in enumerate(myHand.landmark):
                        logging.info("Storing the shape of the landmarks")
                        #Store the shape of the landmarks
                        h , w, c = img.shape

                        logging.info("Converting them into x , y coordinates")
                        #Convert them into x, y coordinates
                        cx ,cy = int(lm.x*w),int(lm.y*h)
                        lmlist.append([id,cx,cy])
                        
            return lmlist
        
        except Exception as e:
            logging.info("Error occured while  finding the position of landmarks")
            raise CustomException(e,sys)
    
    #Create a method to detect whether fingers are up or not
    def fingersUp(self):
        '''
            Returns a dictionary with the status of each finger
            1 : Thumb up
            0: Thunb dawn
            1: Finger up
            0: Finger down
        '''
        try:
            
            logging.info("Defining a list to  store the status of each finger")
            fingers = []
            
            # Thumb
            logging.info("Storing the status of Thumb")
            if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            # Fingers
            for id in range(1, 5):
                
                logging.info("Storing the status of finger")
                if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            return fingers
        
        except Exception as e:
            logging.info("Error occured while  checking the status of fingers")
            raise CustomException(e,sys)

               
def main():
    
    try:

        pTime = 0
        cTime = 0

        logging.info("Creating object for camera")
        cap = cv2.VideoCapture(0)

        logging.info("Creating a object for hand detector class")
        detector = handDetector()

        while True:
            logging.info("Reading the image")
            success , img = cap.read()

            logging.info("Finding the hands")
            img = detector.findHands(img)
            logging.info("Found hands")

            logging.info("Finding the position of the land marks")
            lmlist = detector.findPosition(img)
            logging.info("Found the position")

            cTime = time.time()
            fps = 1/(cTime-pTime)
            pTime = cTime

            logging.info("Writing fps on the frame")
            cv2.putText(img,str(int(fps)),(10,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)

            logging.info("Showing the detected image")
            cv2.imshow("Image", img)

            cv2.waitKey(1)

    except Exception as e:
        logging.info("Error occured while executing the main method")
        raise CustomException(e,sys)

if __name__ == "__main__":
    main()