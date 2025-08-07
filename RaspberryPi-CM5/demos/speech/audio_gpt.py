import os,random
import time
import wave
import numpy as np
import pyaudio
import datetime
from scipy import fftpack
from auto_platform import AudiostreamSource, play_command, default_libpath
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont
import xgoscreen.LCD_2inch as LCD_2inch
import logging
from key import language
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
#version=2.0

# Display Init
display = LCD_2inch.LCD_2inch()
display.Init()
display.clear()

# Init Splash
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

def lcd_draw_string(splash, x, y, text, color=(255, 255, 255), font_size=1, scale=1, mono_space=False, auto_wrap=True, background_color=(0, 0, 0)):
    splash.text((x, y), text, fill=color, font=scale)


'''
    LCD Rect
'''
def lcd_rect(x, y, w, h, color, thickness):
    draw.rectangle([(x, y), (w, h)], fill=color, width=thickness)
def clear_top():
    draw.rectangle([(0, 0), (320, 111)], fill=splash_theme_color)
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

import sys
sys.path.append('/home/pi/RaspberryPi-CM5/xiaozhi_test')
from wake_word import is_wake_gpt
def start_recording(p, stream_a, audio_stream, timel=3, save_file="recorded_audio.wav"):
    global automark, quitmark
    start_threshold = 220000
    end_threshold = 40000
    endlast = 15
    max_record_time = 5 
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    WAVE_OUTPUT_FILENAME = save_file

    if automark:
        logging.warning(automark)
        frames = []
        start_luyin = False
        break_luyin = False
        data_list = [0] * endlast
        sum_vol = 0
        start_time = None

       
        logging.warning("audio_stream start after")
        
        audio_stream.start()
        logging.warning("audio_stream start")
        
        while not break_luyin:
            if not automark or quitmark == 1:
                break
            #唤醒表情
            #display.ShowImage(splash)
            waked = is_wake_gpt()
            if waked:
                print("lulu detected: " + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"))
                #os.system("aplay /home/pi/RaspberryPi-CM4/demos/speech/voice/ding.wav")
                break
        audio_stream.stop()
        logging.warning("wakeup")
        lcd_rect(30, 40, 320, 90, splash_theme_color, -1)
        stream_a.stop_stream()
        stream_a.start_stream()
        while not break_luyin:
            if not automark or quitmark == 1:
                break
            
            data = stream_a.read(CHUNK, exception_on_overflow=False)
            rt_data = np.frombuffer(data, dtype=np.int16)
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0 : fft_temp_data.size // 2 + 1]
            vol = sum(fft_data) // len(fft_data)
            
            data_list.pop(0)
            data_list.append(vol)
            
            logging.warning(f"当前音量: {vol}, 启动阈值: {start_threshold}, 结束阈值: {end_threshold}")
            
            if vol > start_threshold:
                sum_vol += 1
                if sum_vol == 1:
                    print("start recording")
                    start_luyin = True
                    start_time = time.time()
            
            if start_luyin:
                elapsed_time = time.time() - start_time
                
                if all(float(i) < end_threshold for i in data_list) or elapsed_time > max_record_time:
                    print("录音结束: 低音量 或 录音时间超限")
                    break_luyin = True
                    frames = frames[:-5]
            
            if start_luyin:
                frames.append(data)
            print(start_threshold, vol)
            #倾听表情
            free_anmi("waiting")
            #display.ShowImage(splash)
        print("auto end")
    
    if quitmark == 0:
        try:
            stream_a.stop_stream()
            stream_a.close()
            logging.warning("stream_a stop")
        except:
            pass
        p.terminate()
        logging.warning("p kill")
        wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()
        print(f"录音完成，文件已保存: {WAVE_OUTPUT_FILENAME}")
