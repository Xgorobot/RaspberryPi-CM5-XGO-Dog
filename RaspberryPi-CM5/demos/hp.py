from picamera2 import Picamera2
from uiutils import *
import mediapipe as mp
import cv2
import numpy as np
from PIL import Image

button = Button()
picam2 = Picamera2()

print('aa')
config = picam2.create_preview_configuration(
    main={"size": (320, 240), "format": "BGR888"}
)
picam2.configure(config)
picam2.start()

mpHands = mp.solutions.hands  
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def handDetector(img):
    length = 0
  
    results = hands.process(img)
    
    if results.multi_hand_landmarks:
        for handlms in results.multi_hand_landmarks:
            for index, lm in enumerate(handlms.landmark):
                h, w = img.shape[:2]
                cx, cy = int(lm.x * w), int(lm.y * h)
                if index == 4:
                    x1, y1 = cx, cy
                if index == 8:
                    x2, y2 = cx, cy
                  
                    cv2.circle(img, (x1,y1), 5, (0,0,255), cv2.FILLED) 
                    cv2.circle(img, (x2,y2), 5, (0,0,255), cv2.FILLED) 
                    cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3) 
                    length = ((x1-x2)**2 + (y1-y2)**2)**0.5
                    length = min(int(length), 1000)
    return img, length

while True:
    img = picam2.capture_array()
    img, length = handDetector(img)
    img_pil = Image.fromarray(img)
    display.ShowImage(img_pil)
    
    print(f"Detected finger distance: {length}")
    
    if length > 0:
        h = min(max(length, 0), 100)
        target_height = 75 + (h / 100 * 40)
        dog.translation('z', target_height)
        print(f"Setting height to: {target_height}")
    else:
        dog.translation('z', 95)
        
    if button.press_b():
        dog.reset()
        break

picam2.stop()
