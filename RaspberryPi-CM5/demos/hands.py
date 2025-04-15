from uiutils import Button,display, dog
from PIL import Image
import numpy as np
import cv2, time
import mediapipe as mp
from picamera2 import Picamera2

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
picam2.start()


button = Button()

dogtime = 0

def finger_stretch_detect(point1, point2, point3):
    #Detect if a finger is stretched based on landmark positions.
    dist1 = np.linalg.norm((point2 - point1), ord=2)
    dist2 = np.linalg.norm((point3 - point1), ord=2)
    return 1 if dist2 > dist1 else 0

def detect_hands_gesture(figure):
    #Map finger stretch results to a gesture.
    gestures = {
        (1, 0, 0, 0, 0): "good",
        (0, 1, 0, 0, 0): "one",
        (0, 0, 1, 0, 0): "please civilization in testing",
        (0, 1, 1, 0, 0): "two",
        (0, 1, 1, 1, 0): "three",
        (0, 1, 1, 1, 1): "four",
        (1, 1, 1, 1, 1): "five",
        (1, 0, 0, 0, 1): "six",
        (0, 0, 1, 1, 1): "OK",
        (0, 0, 0, 0, 0): "stone"
    }
    return gestures.get(tuple(figure), "not in detect range...")

def process_gesture(gesture_result):
    #Trigger dog actions based on the detected gesture.
    global dogtime
    if time.time() > dogtime:
        
        actions = {
            "good": 23, "one": 7, "two": 8, "three": 9,
            "four": 22, "five": 1, "six": 24, "OK": 19, "stone": 20}
     
        
        if gesture_result in actions:
            dogtime = time.time()
            dog.action(actions[gesture_result])
            dogtime += 3 

def main():
    #detect gestures, and control the dog.
    while True:
     
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 1)
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_RGB)
        gesture_result = None

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )
                
              
                landmark = np.array([[int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])] for lm in hand_landmarks.landmark])
                
               
                figure = np.array([
                    finger_stretch_detect(landmark[17], landmark[4*k+2], landmark[4*k+4]) if k == 0
                    else finger_stretch_detect(landmark[0], landmark[4*k+2], landmark[4*k+4])
                    for k in range(5)
                ])
                
               
                gesture_result = detect_hands_gesture(figure)

            
            if gesture_result:
                cv2.putText(frame, f"{gesture_result}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)

       
        if gesture_result:
            process_gesture(gesture_result)

        
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        display.ShowImage(img)

        
        if cv2.waitKey(5) & 0xFF == 27 or button.press_b():
            dog.reset()
            break

if __name__ == "__main__":
    main()
