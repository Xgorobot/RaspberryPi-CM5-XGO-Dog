from picamera2 import Picamera2
import time
import cv2 as cv
import numpy as np

class Dog_Camera(object):
    def __init__(self, width=640, height=480, debug=False):
        self.__debug = debug
        self.__state = False
        self.__width = width
        self.__height = height
        print("---------Camera Init...------------")

        self.__picam2 = Picamera2()
        config = self.__picam2.create_preview_configuration(main={"format": 'RGB888', "size": (self.__width, self.__height)})
        self.__picam2.configure(config)
        self.__picam2.start()
        
        self.__state = True
        
        if self.__debug:
            print("---------Camera Init OK!------------")

    def __del__(self):
        if self.__debug:
            print("---------Del Camera!------------")
        self.__picam2.stop()
        self.__state = False

    def isOpened(self):
        return self.__state

    def get_frame(self):
        if self.__state:

            frame = self.__picam2.capture_array()
            return True, frame
        else:
            return False, None

    def get_frame_jpg(self, text="", color=(0, 255, 0)):
        success, image = self.get_frame()
        if not success:
            return success, bytes({1})


        if text != "":
            cv.putText(image, str(text), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        

        success, jpeg = cv.imencode('.jpg', image)
        return success, jpeg.tobytes()

if __name__ == '__main__':
    camera = Dog_Camera(debug=True)
    average = False
    m_fps = 0
    t_start = time.time()
    
    while camera.isOpened():
        if average:
            ret, frame = camera.get_frame()
            m_fps = m_fps + 1
            fps = m_fps / (time.time() - t_start)
        else:
            start = time.time()
            ret, frame = camera.get_frame()
            end = time.time()
            fps = 1 / (end - start)
        
        text = "FPS:" + str(int(fps))
        cv.putText(frame, text, (20, 30), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 0), 1)
        
        cv.imshow('frame', frame)

        k = cv.waitKey(1) & 0xFF
        if k == 27 or k == ord('q'):
            break
    
    del camera
    cv.destroyAllWindows()
