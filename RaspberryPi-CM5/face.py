# coding=utf-8
# 人脸识别类 - 使用face_recognition模块
import cv2
import face_recognition
import os
from key import Button
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
button = Button()
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
picam2.start()
## 先拍照，再识别
def take_photo():
    global i 
    while True:
        frame = picam2.capture_array()
        b, g, r = cv2.split(frame)
        img = cv2.merge((r, g, b))
        imgok = Image.fromarray(img)
        display.ShowImage(imgok) 
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        if button.press_d():
            cv2.imwrite(f"{i}.jpg", frame)
            i += 1
            print("拍照成功")
        if button.press_c():
            print("退出人脸录入模式，开始识别")
            break
        if button.press_b():
            exit()
        

def load_photo(i):
    total_image_name = []
    total_face_encoding = []
    for j in range(1, i): 
        fn = f"{j}.jpg"  # 这里是拍照后保存的图片名
        print(fn)
        # try:
        total_face_encoding.append(face_recognition.face_encodings(face_recognition.load_image_file(fn))[0])
        # except:
        #     print(f"人脸识别失败，图片{fn}中人脸识别不清晰或不存在")
        fn = fn[:(len(fn) - 4)]  #截取图片名（这里应该把images文件中的图片名命名为为人物名）
        total_image_name.append(fn)  #图片名字列表
    return total_image_name, total_face_encoding
face = False
while (1):
    while True:
        if face == True:
            break
        print("开始人脸录入")
        i = 1
        take_photo()
        try:
            total_image_name, total_face_encoding = load_photo(i)
            face = True
            print("人脸录入成功，开始识别")
            break
        except Exception as e:
            print("人脸录入失败，请重新拍照")
            continue
    frame = picam2.capture_array()
    # 发现在视频帧所有的脸和face_enqcodings
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    # 在这个视频帧中循环遍历每个人脸
    for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings):
        # 看看面部是否与已知人脸相匹配。
        for i, v in enumerate(total_face_encoding):
            match = face_recognition.compare_faces(
                [v], face_encoding, tolerance=0.5)
            name = "Unknown"
            if match[0]:
                name = total_image_name[i]
                name = 'NO.' + name
                break
        # 画出一个框，框住脸
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # 画出一个带名字的标签，放在框下
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255),
                      cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        try:
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.7,
                    (255, 255, 255), 1)
        except :
            name = "Unknown"
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.7,
                    (255, 255, 255), 1)
    # 显示结果图像
    b, g, r = cv2.split(frame)
    img = cv2.merge((r, g, b))
    imgok = Image.fromarray(img)
    display.ShowImage(imgok)  
    # cv2.imshow('Video', frame)
    if button.press_b():
    #if cv2.waitKey(1) & 0xFF == ord('q'):
        break
