import pyaudio
import wave
import numpy as np
from scipy import fftpack
import time
import random

# 录音参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 600  # 最大录音时长
SAVE_FILE = "recorded_audio.wav"
START_THRESHOLD = 70000  # 开始录音的音量阈值
END_THRESHOLD = 40000  # 停止录音的音量阈值
ENDLAST = 10

from PIL import Image, ImageDraw, ImageFont
import xgoscreen.LCD_2inch as LCD_2inch
display = LCD_2inch.LCD_2inch()
display.clear()
splash_theme_color = (15, 21, 46)
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)
mic_logo = Image.open("/home/pi/RaspberryPi-CM4/pics/mic.png")
mic_wave = Image.open("/home/pi/RaspberryPi-CM4/pics/mic_wave.png")
mic_purple = (24, 47, 223)
splash_theme_color = (15, 21, 46)

def calculate_volume(data):
    """计算音频数据的音量"""
    rt_data = np.frombuffer(data, dtype=np.int16)
    fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
    fft_data = np.abs(fft_temp_data)[0: fft_temp_data.size // 2 + 1]
    return sum(fft_data) // len(fft_data)

def start_recording(p, stream):

    print("等待声音开始...")
    frames = []
    start_recording_flag = False
    end_data_list = [0] * ENDLAST

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        volume = calculate_volume(data)
        print(f"当前音量: {volume} | 阈值: 开始={START_THRESHOLD} 结束={END_THRESHOLD}", end='\r')
        if not start_recording_flag:
            if volume > START_THRESHOLD:
                print("开始录音...")
                start_recording_flag = True
                frames.append(data)
        else:
            end_data_list.pop(0)
            end_data_list.append(volume)
            frames.append(data)
            if all([vol < END_THRESHOLD for vol in end_data_list]):
                print("录音结束。")
                break

    wf = wave.open(SAVE_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"录音已保存为 {SAVE_FILE}")

if __name__ == "__main__":
     start_recording()
