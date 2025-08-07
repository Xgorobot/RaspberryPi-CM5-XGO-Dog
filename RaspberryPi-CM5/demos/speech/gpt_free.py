import os,time,threading,pyaudio,requests
import xgoscreen.LCD_2inch as LCD_2inch
from xgolib import XGO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from key import Button,language
from audio_gpt import start_recording 
from language_recognize import test_one 
from doubao_gpt import model_output
import logging
import pyttsx3
import threading,random
import asyncio
from volcengine_binary_demo.examples.volcengine.binary import main
from src.auto_platform import play_command
#init
la=language()
SPLASH_COLOR = (15, 21, 46)
FONT_PATH = "/home/pi/model/msyh.ttc"
FONT_SIZE = 20
DOG_PORT = '/dev/ttyAMA0'
DOG_VERSION = "xgomini"
TEST_NETWORK_URL = "http://www.baidu.com"

WIFI_OFFLINE_PATH = "/home/pi/RaspberryPi-CM5/pics/offline.png"
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 22)
color_white = (255, 255, 255)
mic_purple = (24, 47, 223)
ani_num = 0
play_anmi = True
quitmark = 0
import pyaudio
from auto_platform import AudiostreamSource
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class GPTFREE:
    def __init__(self):
        self.display = LCD_2inch.LCD_2inch()
        self.display.Init()
        
        self.splash = Image.new("RGB", (self.display.height, self.display.width), SPLASH_COLOR)
        self.draw = ImageDraw.Draw(self.splash)
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        
        self.dog = XGO(port=DOG_PORT, version=DOG_VERSION)
        self.button = Button()
        self.audio_stream = None
        self.stream_a = None
        self.p = None
        self.network_available = False
        
        # 启动按键检测线程
        self._start_button_thread()
        try:
            wifi_img = Image.open(WIFI_OFFLINE_PATH)
            self.nowifi_image = Image.new("RGB", wifi_img.size, SPLASH_COLOR)
            self.nowifi_image.paste(wifi_img, (0, 0), wifi_img)  
        except Exception as e:
            print(f"加载图片失败: {e}")
            self.nowifi_image = Image.new("RGB", (100, 100), (255, 0, 0))  
    def _start_button_thread(self):
        def check_button():
            while True:
                if self.button.press_b():
                    try:
                        if self.audio_stream:
                            self.audio_stream.stop()
                            logging.warning('audio_stream kill')
                    except Exception as e:
                        logging.warning(e)
                    try:
                        if self.stream_a:
                            self.stream_a.stop_stream()
                            self.stream_a.close()
                            logging.warning("stream_a kill")
                    except Exception as e:
                        logging.warning(e)
                    try:
                        if self.p:
                            self.p.terminate()
                            logging.warning("p terminate")
                    except:
                        pass
                    print("B键按下, 退出程序")
                    os._exit(0)
                time.sleep(0.1)
        
        thread = threading.Thread(target=check_button, daemon=True)
        thread.start()

    def show_message(self, text, color=(255, 255, 255)):
        self.draw.rectangle((0, 0, self.display.height, self.display.width), fill=SPLASH_COLOR)
        self.draw.text((80, 100), text, fill=color, font=self.font)
        self.display.ShowImage(self.splash)

    def execute_action(self, action_name):
        if action_name in ACTION_MAP:
            action_id, duration = ACTION_MAP[action_name]
            self.dog.action(action_id)
            time.sleep(duration)
            return True
        return False

    def check_network(self):
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            try:
                requests.get(TEST_NETWORK_URL, timeout=1)
                print("Net is connected")
                self.network_available = True
                return True  # 直接返回True，不显示任何内容
            except:
                print(f"Network connection attempt {attempt + 1} failed")
                attempt += 1
                time.sleep(1)
        
        print("Network connection failed after 5 attempts")
        self.network_available = False
        self.draw.rectangle((0, 0, self.display.height, self.display.width), fill=SPLASH_COLOR)
        img_width, img_height = self.nowifi_image.size
        x_pos = (self.display.height - img_width) // 2
        y_pos = 40
        self.splash.paste(self.nowifi_image, (x_pos, y_pos))
        if la == "cn":
            text = "WIFI未连接或无网络"
        else:
            text = "WIFI is not connected"
        text_width = self.draw.textlength(text, font=font2)
        x_position = (self.display.height - text_width) // 2
        self.draw.text((x_position, 170), text, fill=color_white, font=font2)
        self.display.ShowImage(self.splash)
        
        return False
    
    def free_anmi(self,kinds):
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
        self.display.ShowImage(exp)

    def recog_anmi(self):
        global play_anmi,quitmark
        print("recog_anmi", play_anmi)
        while 1:
            self.free_anmi("recog")
            time.sleep(0.03)
            if play_anmi == False:
                break
            if quitmark:
                break


    def speak_anmi(self):
        global play_anmi,quitmark
        rn = random.randint(1, 4)
        while 1:
            if rn == 1:
                self.free_anmi("speak1")
            elif rn == 2:
                self.free_anmi("speak2")
            elif rn == 3:
                self.free_anmi("speak3")
            elif rn == 4:
                self.free_anmi("speak4")
            time.sleep(0.02)
            if play_anmi == False:
                break
            if quitmark:
                break
    def clean_text(self,text):
        text = text.replace("…", "...").replace("！", "!").replace("，", ",")
        return text
    

    def run(self):
        """Main program loop"""
        # Check network connection
        if not self.check_network():
            while True:
                time.sleep(1)
            return
        
        # Show startup message
        startup_msg = "正在启动，请稍后" if la == "cn" else "Starting up..."
        self.show_message(startup_msg, color=color_white)
        
        # Main interaction loop
        while True:
            try:
                # Initialize audio
                self.p = pyaudio.PyAudio()
                self.stream_a = self.p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                )
                self.audio_stream = AudiostreamSource()
                logging.warning('音频初始化完成')
                
                # Start recording
                start_recording(self.p, self.stream_a, self.audio_stream)
                logging.warning("录音结束")
                
                # Speech recognition
                content = test_one()
                if not content:
                    print("录音出错")
                    continue
                
                print("识别内容:", content)
                
                # Get model response
                print("正在调用 model_output...") 
                speech_results = model_output(content=content)
                speech_results = self.clean_text(speech_results)
                print("模型回复:", speech_results)
                
                # Display the response
                if speech_results:
                    # Start speaking animation in a separate thread
                    global play_anmi
                    play_anmi = True
                    animation_thread = threading.Thread(target=self.speak_anmi, daemon=True)
                    animation_thread.start()
                    async def run_tts():
                        await main(
                            text=speech_results,
                            voice_type="zh_female_wanqudashu_moon_bigtts"
                        )
                    
                    asyncio.run(run_tts())
                    os.system(play_command + " /home/pi/RaspberryPi-CM5/gptfree_speak.wav")
                    # Wait for animation to complete (simulating speech time)

                    time.sleep(len(speech_results) * 0.1)  # Adjust timing as needed
                    
                    # Stop animation
                    play_anmi = False
                    animation_thread.join()
                
            except KeyboardInterrupt:
                print("程序终止")
                break
            except Exception as e:
                print(f"发生错误: {e}")
                continue
            finally:
                # Clean up audio resources
                if hasattr(self, 'stream_a') and self.stream_a:
                    self.stream_a.stop_stream()
                    self.stream_a.close()
                if hasattr(self, 'p') and self.p:
                    self.p.terminate()

if __name__ == "__main__":
    controller = GPTFREE()
    try:
        controller.run()
    finally:
        # Clean up TTS engine when program exits
        if hasattr(controller, 'tts_engine') and controller.tts_engine:
            controller.tts_engine.stop()