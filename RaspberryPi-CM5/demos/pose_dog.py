from uiutils import display, Button, dog
from PIL import Image
from picamera2 import Picamera2
import mediapipe as mp
import numpy as np
import cv2
import threading
import time

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
picam2.start()

# Initialize MediaPipe pose detector
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
poses = mp_pose.Pose()

# Initial height and sport tracking
height = 115
quitmark = False
sport = {"count": 0, "calories": 0}
button = Button()


def mode():
    global height, quitmark
    while not quitmark:
        dog.translation("z", height) 
        time.sleep(0.1)


mode_thread = threading.Thread(target=mode)
mode_thread.start()

# Calculate angle between three points
def calc_angles(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return min(angle, 360 - angle)

# Get specific body landmark coordinates
def get_landmark(landmarks, part_name):
    landmark = landmarks[mp_pose.PoseLandmark[part_name].value]
    return [landmark.x, landmark.y, landmark.z]

# Calculate average knee angle from both legs
def get_knee_angle(landmarks):
    r_hip = get_landmark(landmarks, "RIGHT_HIP")
    l_hip = get_landmark(landmarks, "LEFT_HIP")
    r_knee = get_landmark(landmarks, "RIGHT_KNEE")
    l_knee = get_landmark(landmarks, "LEFT_KNEE")
    r_ankle = get_landmark(landmarks, "RIGHT_ANKLE")
    l_ankle = get_landmark(landmarks, "LEFT_ANKLE")
    r_angle = calc_angles(r_hip, r_knee, r_ankle)
    l_angle = calc_angles(l_hip, l_knee, l_ankle)
    return (r_angle + l_angle) / 2  

# Main loop to process video and track knee angle
def main():
    global height, quitmark, sport
    start_time = 0
    status = False

    while not quitmark:
        frame = picam2.capture_array() 
        frame = cv2.flip(frame, 1) 
        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        poseoutput = poses.process(rgbframe)  

        if poseoutput.pose_landmarks:
          
            mp_drawing.draw_landmarks(frame, poseoutput.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            knee_angle = get_knee_angle(poseoutput.pose_landmarks.landmark)
            height = int(115 - (180 - knee_angle) / 90 * 40)

            # Track squat status and calculate sport data (count and calories)
            if status:
                if knee_angle > 160:
                    status = False
                    elapsed_time = time.time() - start_time
                    if 3 < elapsed_time < 3000:
                        sport["count"] += 1
                        sport["calories"] += int(0.66 * elapsed_time)
            else:
                if knee_angle < 120:
                    start_time = time.time()
                    status = True

           
            color = (0, 255, 0) if status else (0, 0, 255)
            cv2.putText(frame, f"Height: {height}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Angle: {knee_angle:.1f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


     
        imgok = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        display.ShowImage(imgok)

       
        if button.press_b():
            quitmark = True
            break

    
    dog.reset()
    picam2.stop()


main()
