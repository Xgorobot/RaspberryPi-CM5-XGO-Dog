
import cv2
from keras.models import load_model
import numpy as np
#import chineseText
import datetime
from PIL import Image, ImageDraw
import xgoscreen.LCD_2inch as LCD_2inch
splash_theme_color = (255,255,255)
display = LCD_2inch.LCD_2inch()
display.Init()
display.clear()
# Init Splash
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)
startTime = datetime.datetime.now()
emotion_classifier = load_model(
   '/home/pi/RaspberryPi-CM4/simple_CNN.985-0.66.hdf5')
endTime = datetime.datetime.now()
print(endTime - startTime)

emotion_labels = {
    0: '生气',
    1: '厌恶',
    2: '恐惧',
    3: '开心',
    4: '难过',
    5: '惊喜',
    6: '平静'
}
from PIL import ImageFont
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
picam2.start()
print("摄像头初始化完毕")
while True:
    img = picam2.capture_array()
# img = cv2.imread("img/emotion/emotion.png")
    face_classifier = cv2.CascadeClassifier(
        "C:\Python36\Lib\site-packages\opencv-master\data\haarcascades\haarcascade_frontalface_default.xml"
    )
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=3, minSize=(40, 40))
    color = (255, 0, 0)

    for (x, y, w, h) in faces:
        gray_face = gray[(y):(y + h), (x):(x + w)]
        gray_face = cv2.resize(gray_face, (48, 48))
        gray_face = gray_face / 255.0
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
        emotion = emotion_labels[emotion_label_arg]
        cv2.rectangle(img, (x + 10, y + 10), (x + h - 10, y + w - 10),
                    (255, 255, 255), 2)
        cv2.putText(img, emotion, (x + h * 0.3, y), font, 0.7,
                    color, 1)
        #img = chineseText.cv2ImgAddText(img, emotion, x + h * 0.3, y, color, 20)
    b, g, r = cv2.split(img)
    img = cv2.merge((r, g, b))
    imgok = Image.fromarray(img)
    display.ShowImage(imgok)  

