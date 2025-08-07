from statistics import mode
import time
import os
import sys
from PIL import Image, ImageDraw
import xgoscreen.LCD_2inch as LCD_2inch
from pygame import mixer  # 导入pygame的mixer模块用于音频播放
import cv2
from keras.models import load_model
import numpy as np

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input

# 初始化音频 mixer
mixer.init()
# 设置音量 (0.0 到 1.0)
mixer.music.set_volume(1.0)

splash_theme_color = (255,255,255)
display = LCD_2inch.LCD_2inch()
display.Init()
display.clear()
# Init Splash
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

# parameters for loading data and images
detection_model_path = '/home/pi/RaspberryPi-CM5/face_classification-master/trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = '/home/pi/RaspberryPi-CM5/face_classification-master/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []

# starting video streaming
from key import Button
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
picam2.start()
print("摄像头初始化完毕")
button = Button()

# 文件路径配置
pic_path = "/home/pi/RaspberryPi-CM5/demos/expression/"
audio_path = "/home/pi/RaspberryPi-CM5/face_classification-master/src/audio/"  # 音频文件存放路径

# 情绪与音频文件名映射
emotion_audio_map = {
    "angry": "angry.mp3",
    "sad": "sad.mp3",
    "happy": "happy.mp3",
    "surprise": "surprise.mp3",
    "neutral": "neutral.mp3"
    # "fear": "fear.mp3",  # 恐惧对应的情绪标签可能是fear
    # "disgust": "disgust.mp3"  # 厌恶对应的情绪标签可能是disgust
}

def play_audio(emotion):
    """播放对应情绪的音频"""
    try:
        if emotion in emotion_audio_map:
            audio_file = os.path.join(audio_path, emotion_audio_map[emotion])
            if os.path.exists(audio_file):
                # 停止当前播放的音频
                mixer.music.stop()
                # 加载并播放新音频
                mixer.music.load(audio_file)
                mixer.music.play()
                return True
        print(f"情绪 {emotion} 对应的音频文件不存在")
        return False
    except Exception as e:
        print(f"播放音频时出错: {e}")
        return False

def show(expression_name_cs, pic_num, emotion=None):
    """显示表情图片并播放对应音频"""
    global canvas
    # 如果提供了情绪参数，播放对应音频
    if emotion:
        play_audio(emotion)
    
    for i in range(0, pic_num):
        try:
            exp = Image.open(pic_path + expression_name_cs + "/" + str(i + 1) + ".png")
            display.ShowImage(exp)
            time.sleep(0.1)
            if button.press_b():
                sys.exit()
        except Exception as e:
            print(f"显示图片时出错: {e}")
Count = 10
Count_num = 0
last_emotion = None
while True:
    bgr_image = picam2.capture_array()
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    faces = detect_faces(face_detection, gray_image)

    for face_coordinates in faces:

        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = emotion_classifier.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)
        emotion_text = emotion_labels[emotion_label_arg]
        emotion_window.append(emotion_text)
        if emotion_text != last_emotion:
            Count_num = 0
        else:
            Count_num += 1
        last_emotion = emotion_text

        if len(emotion_window) > frame_window:
            emotion_window.pop(0)
        try:
            emotion_mode = mode(emotion_window)
        except:
            continue

        print(f"当前的情绪为: {emotion_text},概率为{emotion_probability},连续计数为: {Count_num}")
        if emotion_text == 'angry' and Count_num >= Count :
            color = emotion_probability * np.asarray((255, 0, 0))
            show("angry", 13, "angry")
            Count_num = 0
        elif emotion_text == 'sad' and Count_num >= Count :
            color = emotion_probability * np.asarray((0, 0, 255))
            show("sad", 14, "sad")
            Count_num = 0
        elif emotion_text == 'happy' and Count_num >= Count :
            color = emotion_probability * np.asarray((255, 255, 0))
            show("happy", 12, "happy")
            Count_num = 0
        elif emotion_text == 'surprise' and Count_num >= Count :
            color = emotion_probability * np.asarray((0, 255, 255))
            show("surprise", 15, "surprise")
            Count_num = 0
        elif emotion_text == 'neutral' and Count_num >= Count :
            color = emotion_probability * np.asarray((0, 255, 255))
            show("naughty", 14, "neutral")
            Count_num = 0
        else:
            color = emotion_probability * np.asarray((0, 255, 0))
            # # 假设其他情绪为恐惧和厌恶
            # if emotion_text in ['fear', 'scared']:  # 根据实际标签调整
            #     show("Stun", 8, "fear")  # 恐惧
            # elif emotion_text in ['disgust', 'repulsed']:  # 根据实际标签调整
            #     show("shame", 11, "disgust")  # 厌恶

        color = color.astype(int)
        color = color.tolist()
        
        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, emotion_mode,
                  color, 0, -45, 1, 1)

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    b, g, r = cv2.split(bgr_image)
    img = cv2.merge((r, g, b))
    imgok = Image.fromarray(img)
    display.ShowImage(imgok)  
    if button.press_b():
        break

# 程序结束时停止音频并清理资源
mixer.music.stop()
mixer.quit()