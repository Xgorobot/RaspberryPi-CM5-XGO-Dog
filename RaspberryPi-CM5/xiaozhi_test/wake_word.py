import os,random
import numpy as np
from scipy import fftpack
import xgoscreen.LCD_2inch as LCD_2inch
import logging
from key import language
import pyaudio
from pypinyin import lazy_pinyin
from src.constants.constants import AudioConfig
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import time
from PIL import Image, ImageDraw, ImageFont
la=language()
mic_logo = Image.open("/home/pi/RaspberryPi-CM5/pics/mic.png")
mic_wave = Image.open("/home/pi/RaspberryPi-CM5/pics/mic_wave.png")
mic_purple = (24, 47, 223)
splash_theme_color = (15, 21, 46)
font2=ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
quitmark = 0
automark = True
ani_num = 0
play_anmi = True
# Display Init
display = LCD_2inch.LCD_2inch()
display.Init()
display.clear()

# Init Splash
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

sample_rate = AudioConfig.INPUT_SAMPLE_RATE
wake_words = ["您好", "你好", "露露","哈喽","嗨","hello", "hey", "hi"]
wake_words_pinyin = []

for word in wake_words:
    wake_words_pinyin.append(''.join(lazy_pinyin(word)))
print(f"唤醒词拼音列表: {wake_words_pinyin}")
    
def lcd_draw_string(splash, x, y, text, color=(255, 255, 255), font_size=1, scale=1, mono_space=False, auto_wrap=True, background_color=(0, 0, 0)):
    splash.text((x, y), text, fill=color, font=scale)

def show_words_dog():
    if la=="cn":
      lcd_draw_string(draw, 60, 125, "请说‘你好，lulu’进行唤醒", color=(0, 255, 255), scale=font2, mono_space=False)
      lcd_draw_string(draw, 10, 150, "跳舞|俯卧撑|撒尿|伸懒腰|祈祷|鸡头|找食物", color=(0, 255, 255), scale=font2, mono_space=False)
      lcd_draw_string(draw, 10, 170, "向下抓取|波浪|乞讨", color=(0, 255, 255), scale=font2, mono_space=False)
    else:
      lcd_draw_string(draw, 25, 125, "Please say 'hello, lulu' to wake up", color=(0, 255, 255), scale=font2, mono_space=False)
      lcd_draw_string(draw, 10, 150, "Dance|PushUp|Pee|Strech|Pray|Beg", color=(0, 255, 255), scale=font2, mono_space=False)
      lcd_draw_string(draw, 10, 170, "LookingForFood|GrabDown|Wave", color=(0, 255, 255), scale=font2, mono_space=False)
      lcd_draw_string(draw, 10, 190, "ChickenHead", color=(0, 255, 255), scale=font2, mono_space=False)
      
def visual(content):
    gray_color = (128, 128, 128)
    rectangle_x = (display.width - 120) // 2 
    rectangle_y = 110  
    rectangle_width = 200
    rectangle_height = 80
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=gray_color)
    def lcd_draw_string(
            splash,
            x,
            y,
            text,
            color=(255, 255, 255),
            font_size=16,
            max_width=220,
            max_lines=5,
            clear_area=False
    ):
        font = ImageFont.truetype("/home/pi/model/msyh.ttc", font_size)
        line_height = font_size + 2
        total_height = max_lines * line_height
        if clear_area:
            draw.rectangle((x, y, x + max_width, y + total_height), fill=(15, 21, 46))
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        if max_lines:
            lines = lines[:max_lines]

        for i, line in enumerate(lines):
            splash.text((x, y + i * line_height), line, fill=color, font=font)

    lcd_draw_string(
        draw,
        x=70,
        y=115,
        text=content,
        color=(255, 255, 255),
        font_size=16,
        max_width=190,
        max_lines=5,
        clear_area=False
    )
    

def audio_init(audio_stream=None):
    """
    初始化音频流
    :param audio_stream: 音频流对象
    """
    if audio_stream:
        stream = audio_stream
        audio = None
        external_stream = True
        print("唤醒词检测器使用外部音频流")
    else:
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=AudioConfig.INPUT_FRAME_SIZE
        )
        print("唤醒词检测器使用内部音频流")
    return stream
def model_init(model_path="/home/pi/RaspberryPi-CM5/xiaozhi_test/models/vosk-model-small-cn-0.22/"):
    global sample_rate
    """
    初始化模型
    :param model_path: 模型路径
    """
    model_path = "models/vosk-model-small-cn-0.22" if model_path is None else model_path
    model = Model(model_path=model_path)
    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetWords(True)
    print("模型加载完成")
    return model, recognizer
    # 这里可以添加加载模型的代码
def check_and_handle_wake_word(text, is_partial=False):
    detected, wake_word = check_wake_word(text)
    print(f"检测到唤醒词: {detected}, 唤醒词: {wake_word}")
    if detected:
        # 日志记录
        text_type = "部分文本" if is_partial else "完整文本"
        log_msg = f"检测到唤醒词: '{wake_word}' ({text_type}: {text})"
        print(log_msg)
        return True
    else:
        return False
def check_wake_word(text):
    """检查文本中是否包含唤醒词（仅使用拼音匹配）"""
    # 将输入文本转换为拼音
    text_pinyin = ''.join(lazy_pinyin(text))
    text_pinyin = text_pinyin.replace(" ", "")  # 移除空格
    # 只进行拼音匹配
    for i, pinyin in enumerate(wake_words_pinyin):
        if pinyin in text_pinyin:
            return True, wake_words[i]

    return False, None
# model, recognizer = model_init()
if la=="cn":
  model, recognizer = model_init(model_path = "/home/pi/RaspberryPi-CM5/xiaozhi_test/models/vosk-model-small-cn-0.22/")  
else:
  model, recognizer = model_init(model_path = '/home/pi/RaspberryPi-CM5/xiaozhi_test/models/vosk-model-small-en-us-0.15/')  

def process_audio_data(data, model, recognizer):
    recognizer.SetWords(True)
    is_final = recognizer.AcceptWaveform(data)

    # 处理部分结果，实现实时唤醒词检测
    partial_result = json.loads(recognizer.PartialResult())
    partial_text = partial_result.get('partial', '')
    print(f"Partial result: {partial_text}")
    if partial_text.strip():
        waked = check_and_handle_wake_word(partial_text, is_partial=True)

    # 处理最终结果
    if is_final:
        result = json.loads(recognizer.Result())
        if "text" in result and result["text"].strip():
            text = result["text"]
            waked = check_and_handle_wake_word(text, is_partial=False)
            return waked

import os
from src.auto_platform import play_command

def is_wake():
    """唤醒词检测主循环"""
    stream = audio_init()
    print("唤醒词检测循环已启动")
    # 读取音频数据
    while True:
        try:
            # 读取并处理音频数据
            
            data = stream.read(
                sample_rate // 2, 
                exception_on_overflow=False
            )
            if data is None:
                continue
        except (OSError, Exception) as e:
            print(f"音频流读取错误: {e}")

        if len(data) == 0:
            continue
        # 处理音频数据
        waked = process_audio_data(data, model, recognizer)
        if waked:
            os.system(play_command + " /home/pi/RaspberryPi-CM5/ding.wav")
            return True
            
def free_anmi(kinds):
    global ani_num,quitmark
    if kinds == "after":
        pic_path = "./demos/speech/gptfree/"
        expression_name_cs = "after"
        pic_num = 30
    elif kinds == "before":
        pic_path = "./demos/speech/gptfree/"
        expression_name_cs = "before"
        pic_num = 42
    elif kinds == "recog":
        pic_path = "./demos/speech/gptfree/"
        expression_name_cs = "recog"
        pic_num = 90
    elif kinds == "speak1":
        expression_name_cs = "speak"
        pic_path = "./demos/speech/gptfree/speak1/"
        pic_num = 74
    elif kinds == "speak2":
        expression_name_cs = "speak"
        pic_path = "./demos/speech/gptfree/speak2/"
        pic_num = 53
    elif kinds == "speak3":
        expression_name_cs = "speak"
        pic_path = "./demos/speech/gptfree/speak3/"
        pic_num = 86
    elif kinds == "speak4":
        expression_name_cs = "speak"
        pic_path = "./demos/speech/gptfree/speak4/"
        pic_num = 87
    elif kinds == "waiting":
        pic_path = "./demos/speech/gptfree/"
        expression_name_cs = "waiting"
        pic_num = 114

    ani_num += 1
    if ani_num >= pic_num:
        ani_num = 0
    exp = Image.open(pic_path + expression_name_cs + str(ani_num + 1) + ".png")
    display.ShowImage(exp)
    
def draw_wave(ch):
    """Helper function to draw wave visualization (only affects top part)"""
    if ch > 10:
        ch = 10
    start_x = 40
    start_y = 32
    width, height = 80, 50
    y_center = height // 2
    current_y = y_center
    previous_point = (0 + start_x, y_center + start_y)
    
    # Clear ONLY the top area where waves appear
    draw.rectangle([(0, 0), (320, 111)], fill=splash_theme_color)
    
    # Draw mic icon
    draw.bitmap((145, 40), mic_logo, mic_purple)
    
    # Draw left wave
    x = 0
    while x < width:
        segment_length = random.randint(7, 25)
        gap_length = random.randint(4, 20)

        for _ in range(segment_length):
            if x >= width:
                break
            amplitude_change = random.randint(-ch, ch)
            current_y += amplitude_change
            if current_y < 0:
                current_y = 0
            elif current_y > height - 1:
                current_y = height - 1
            current_point = (x + start_x, current_y + start_y)
            draw.line([previous_point, current_point], fill=mic_purple)
            previous_point = current_point
            x += 1
        
        for _ in range(gap_length):
            if x >= width:
                break
            current_point = (x + start_x, y_center + start_y)
            draw.line([previous_point, current_point], fill=mic_purple, width=2)
            previous_point = current_point
            x += 1
    
    # Draw right wave
    start_x = 210
    current_y = y_center
    previous_point = (0 + start_x, y_center + start_y)
    x = 0
    while x < width:
        segment_length = random.randint(7, 25)
        gap_length = random.randint(4, 20)
        for _ in range(segment_length):
            if x >= width:
                break
            amplitude_change = random.randint(-ch, ch)
            current_y += amplitude_change
            if current_y < 0:
                current_y = 0
            elif current_y > height - 1:
                current_y = height - 1
            current_point = (x + start_x, current_y + start_y)
            draw.line([previous_point, current_point], fill=mic_purple)
            previous_point = current_point
            x += 1
        for _ in range(gap_length):
            if x >= width:
                break
            current_point = (x + start_x, y_center + start_y)
            draw.line([previous_point, current_point], fill=mic_purple, width=2)
            previous_point = current_point
            x += 1
def is_wake_wave_speech():
    """唤醒词检测主循环"""
    stream = audio_init()
    print("唤醒词检测循环已启动")
    
    # Initialize display for wave visualization
    draw = ImageDraw.Draw(splash)
    

    # 读取音频数据
    while True:
        try:
            # 读取并处理音频数据
            data = stream.read(
                sample_rate // 2, 
                exception_on_overflow=False
            )
            if data is None:
                continue
                
            # Calculate volume for wave visualization
            rt_data = np.frombuffer(data, dtype=np.int16)
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0 : fft_temp_data.size // 2 + 1]
            vol = sum(fft_data) // len(fft_data)
            
            # Update wave visualization (only affects top part)
            draw_wave(int(vol / 10000))
            show_words_dog()
            # Show the complete image (waves on top + persistent content below)
            display.ShowImage(splash)
            
        except (OSError, Exception) as e:
            print(f"音频流读取错误: {e}")

        if len(data) == 0:
            continue
            
        # 处理音频数据
        waked = process_audio_data(data, model, recognizer)
        if waked:
            os.system(play_command + " /home/pi/RaspberryPi-CM5/ding.wav")
            return True

def is_wake_wave_ei():
    """唤醒词检测主循环"""
    stream = audio_init()
    print("唤醒词检测循环已启动")
    
    # Initialize display for wave visualization
    draw = ImageDraw.Draw(splash)
    

    # 读取音频数据
    while True:
        try:
            # 读取并处理音频数据
            data = stream.read(
                sample_rate // 2, 
                exception_on_overflow=False
            )
            if data is None:
                continue
                
            # Calculate volume for wave visualization
            rt_data = np.frombuffer(data, dtype=np.int16)
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0 : fft_temp_data.size // 2 + 1]
            vol = sum(fft_data) // len(fft_data)
            
            # Update wave visualization (only affects top part)
            draw_wave(int(vol / 10000))
            if la=="cn":
              visual(content='请说:“你好，lulu”唤醒机器人')
            else:
              visual(content="Please say: 'Hello,lulu' to wake up the robot.")
            # Show the complete image (waves on top + persistent content below)
            display.ShowImage(splash)
            
        except (OSError, Exception) as e:
            print(f"音频流读取错误: {e}")

        if len(data) == 0:
            continue
            
        # 处理音频数据
        waked = process_audio_data(data, model, recognizer)
        if waked:
            os.system(play_command + " /home/pi/RaspberryPi-CM5/ding.wav")
            return True

def is_wake_gpt():
    """唤醒词检测主循环"""
    stream = audio_init()
    print("唤醒词检测循环已启动")
    #刷新屏幕
    draw = ImageDraw.Draw(splash)

    # 读取音频数据
    while True:
        try:
            # 读取并处理音频数据
            data = stream.read(
                sample_rate // 2, 
                exception_on_overflow=False
            )
            if data is None:
                continue
            #加入待唤醒表情
            free_anmi("before")
        except (OSError, Exception) as e:
            print(f"音频流读取错误: {e}")

        if len(data) == 0:
            continue
        # 处理音频数据
        waked = process_audio_data(data, model, recognizer)
        if waked:
            os.system(play_command + " /home/pi/RaspberryPi-CM5/ding.wav")
            return True