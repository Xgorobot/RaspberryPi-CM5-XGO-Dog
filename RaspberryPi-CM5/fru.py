import os
import sys
import time
import logging
import random
import spidev as SPI
from pygame import mixer
sys.path.append("..")
import xgoscreen.LCD_2inch as LCD_2inch
from PIL import Image, ImageDraw, ImageFont

FRUIT_MUSIC = "/home/pi/RaspberryPi-CM5/fruits.wav"
BACKGROUND_MUSIC = "/home/pi/RaspberryPi-CM5/background.mp3"
WIN_SOUND = "/home/pi/RaspberryPi-CM5/win.wav"

splash_theme_color = (255, 255, 255)

FRUIT_IMAGE_DIR = "fruits"
os.makedirs(FRUIT_IMAGE_DIR, exist_ok=True)

font_large = ImageFont.truetype("/home/pi/model/msyh.ttc", 24)
font_medium = ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
font_small = ImageFont.truetype("/home/pi/model/msyh.ttc", 12)

class FruitSlotMachine:
    def __init__(self, language='cn'):
        self.language = language
        self.display = LCD_2inch.LCD_2inch()
        self.display.Init()
        self.display.clear()
        
        self.init_audio()
        
        self.splash = Image.new("RGB", (self.display.height, self.display.width), splash_theme_color)
        self.draw = ImageDraw.Draw(self.splash)
        self.display.ShowImage(self.splash)
        
        self.screen_width = self.display.height
        self.screen_height = self.display.width
        
        self.fruits = [
            {"name": "苹果", "image": "apple.png", "value": 5},
            {"name": "橙子", "image": "orange.png", "value": 4},
            {"name": "柠檬", "image": "lemon.png", "value": 3},
            {"name": "西瓜", "image": "watermelon.png", "value": 6},
            {"name": "葡萄", "image": "grape.png", "value": 4},
            {"name": "草莓", "image": "strawberry.png", "value": 5},
            {"name": "樱桃", "image": "cherry.png", "value": 7},
            {"name": "桃子", "image": "peach.png", "value": 3}
        ]
        
        self.slot_count = 3
        self.balance = 100
        self.bet_amount = 10
        self.spinning = False
        self.current_slots = [random.choice(self.fruits) for _ in range(self.slot_count)]
        self.result_text = ""
        self.insufficient_funds = False
        
        # Language strings
        self.texts = {
            'cn': {
                'title': "水果拉霸机",
                'balance': "余额",
                'bet': "下注",
                'controls_title': "按键操作",
                'controls': "A=开始  D=加下注  C=减下注  B=退出",
                'jackpot': "大满贯! 赢 ${}!",
                'win': "中奖! 赢 ${}!",
                'try_again': "再接再厉!",
                'insufficient': "余额不足!",
                'reset': "余额不足，重置游戏"
            },
            'en': {
                'title': "Fruit Slot Machine",
                'balance': "Balance",
                'bet': "Bet",
                'controls_title': "Controls",
                'controls': "A=Spin  D=Increase  C=Decrease  B=Exit",
                'jackpot': "Jackpot! Won ${}!",
                'win': "Win! Won ${}!",
                'try_again': "Try again!",
                'insufficient': "Insufficient funds!",
                'reset': "Low balance, reset game"
            }
        }
        
        self.load_fruit_images()
        self.draw_game_screen()
        self.play_background_music()
    
    def t(self, key, *args):
        """Get translated text with optional formatting"""
        text = self.texts[self.language].get(key, key)
        if args:
            return text.format(*args)
        return text
    
    def init_audio(self):
        try:
            mixer.init(frequency=44100, size=-16, channels=2, buffer=256)
            mixer.music.set_volume(0.4)
            self.sound_volume = 0.7
            
            self.audio_files = {
                "spin": FRUIT_MUSIC,
                "background": BACKGROUND_MUSIC,
                "win": WIN_SOUND
            }
            self.audio_available = {k: os.path.exists(v) for k, v in self.audio_files.items()}
            
            self.win_sound = None
            if self.audio_available["win"]:
                try:
                    self.win_sound = mixer.Sound(WIN_SOUND)
                    self.win_sound.set_volume(self.sound_volume)
                except Exception as e:
                    logging.error(f"Failed to load win sound: {e}")
                    self.audio_available["win"] = False
            
            for typ, available in self.audio_available.items():
                if available:
                    logging.info(f"Loaded {typ} audio: {self.audio_files[typ]}")
                else:
                    logging.warning(f"Missing {typ} audio file: {self.audio_files[typ]}")
                    
        except Exception as e:
            self.audio_available = {"spin": False, "background": False, "win": False}
            logging.error(f"Audio initialization failed: {e}")
    
    def play_background_music(self):
        if not self.audio_available["background"] or self.spinning:
            return
            
        try:
            if not mixer.music.get_busy():
                mixer.music.load(BACKGROUND_MUSIC)
                mixer.music.play(-1)
                logging.info("Background music started")
        except Exception as e:
            logging.warning(f"Background music failed: {e}")
    
    def play_spin_music(self):
        if not self.audio_available["spin"]:
            return
        try:
            mixer.music.stop()
            mixer.music.load(FRUIT_MUSIC)
            mixer.music.play()
            logging.info("Spin music started")
        except Exception as e:
            logging.warning(f"Spin music failed: {e}")
    
    def play_win_sound(self):
        if self.win_sound and self.audio_available["win"]:
            try:
                if mixer.music.get_busy():
                    mixer.music.pause()
                
                self.win_sound.play()
                logging.info("Playing win sound")
                
                while mixer.get_busy():
                    time.sleep(0.1)
                    
                if self.audio_available["background"] and not self.spinning:
                    mixer.music.unpause()
                    
            except Exception as e:
                logging.warning(f"Win sound failed: {e}")
                if self.audio_available["background"] and not self.spinning:
                    try:
                        mixer.music.unpause()
                    except:
                        pass
    
    def load_fruit_images(self):
        for fruit in self.fruits:
            try:
                img_path = os.path.join(FRUIT_IMAGE_DIR, fruit["image"])
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((70, 70), Image.Resampling.LANCZOS)
                fruit["img_obj"] = img
            except Exception as e:
                logging.error(f"Failed to load image {fruit['image']}: {e}")
                fruit["img_obj"] = None
                fruit["fallback_color"] = (random.randint(100, 255), 
                                         random.randint(100, 255), 
                                         random.randint(100, 255))
    
    def draw_game_screen(self):
        self.splash = Image.new("RGB", (self.screen_width, self.screen_height), splash_theme_color)
        self.draw = ImageDraw.Draw(self.splash)
        
        title = self.t('title')
        title_bbox = self.draw.textbbox((0,0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.screen_width - title_width) // 2
        self.draw.text((title_x, 10), title, font=font_large, fill=(139,69,19))
        
        info_color = (255,200,200) if self.insufficient_funds else (240,240,240)
        self.draw.rectangle((10,60, self.screen_width-10,90), fill=info_color, outline=(100,100,100), width=2)
        
        self.draw.text((20,65), f"{self.t('balance')}: ${self.balance}", font=font_medium, fill=(255,0,0) if self.insufficient_funds else (0,0,0))
        bet_text = f"{self.t('bet')}: ${self.bet_amount}"
        bet_bbox = self.draw.textbbox((0,0), bet_text, font=font_medium)
        bet_width = bet_bbox[2] - bet_bbox[0]
        self.draw.text((self.screen_width-20 - bet_width, 65), bet_text, font=font_medium, fill=(0,0,0))
        
        self.draw_slots()
        self.draw_controls()
        
        if self.result_text:
            result_bbox = self.draw.textbbox((0,0), self.result_text, font=font_medium)
            result_width = result_bbox[2] - result_bbox[0]
            result_x = (self.screen_width - result_width) // 2
            self.draw.text((result_x, 220), self.result_text, font=font_medium, fill=(255,0,0) if self.t('try_again') in self.result_text else (0,128,0))
        
        self.display.ShowImage(self.splash)
    
    def draw_slots(self):
        slot_size = 80
        gap = 20
        total_width = slot_size*3 + gap*2
        start_x = (self.screen_width - total_width) // 2
        start_y = 110
        
        for i in range(3):
            x = start_x + i*(slot_size + gap)
            self.draw.rectangle((x, start_y, x+slot_size, start_y+slot_size), fill=(255,255,255), outline=(184,134,11), width=3)
            
            fruit = self.current_slots[i]
            if fruit["img_obj"]:
                self.splash.paste(fruit["img_obj"], (x+5, start_y+5), fruit["img_obj"])
            else:
                self.draw.ellipse((x+5, start_y+5, x+75, start_y+75), fill=fruit["fallback_color"], outline=(255,255,255), width=2)
    
    def draw_controls(self):
        self.draw.text((30, 260), self.t('controls_title') + ":", font=font_small, fill=(100,100,100))
        self.draw.text((30, 280), self.t('controls'), font=font_small, fill=(100,100,100))
    
    def spin(self):
        if self.spinning:
            return
            
        if self.balance < self.bet_amount:
            self.show_insufficient_funds()
            return
            
        self.spinning = True
        self.result_text = ""
        self.balance -= self.bet_amount
        self.draw_game_screen()
        
        self.play_spin_music()
        
        target_slots = [random.choice(self.fruits) for _ in range(3)]
        spin_time = 2000
        steps = 40
        for step in range(steps):
            if step < 28:
                self.current_slots = [random.choice(self.fruits) for _ in range(3)]
            elif step < 36:
                for i in range(3):
                    if step > 28 + i*4:
                        self.current_slots[i] = target_slots[i]
                    else:
                        self.current_slots[i] = random.choice(self.fruits)
            else:
                self.current_slots = target_slots
            
            self.draw_game_screen()
            time.sleep(spin_time/steps/1000)
        
        self.spinning = False
        self.check_win()
        self.draw_game_screen()
        
        self.play_background_music()
    
    def check_win(self):
        fruit_names = [f["name"] for f in self.current_slots]
        if all(n == fruit_names[0] for n in fruit_names):
            win = self.bet_amount *5
            self.balance += win
            self.result_text = self.t('jackpot', win)
            self.play_win_sound()
        elif len(set(fruit_names)) == 2:
            win = self.bet_amount *2
            self.balance += win
            self.result_text = self.t('win', win)
            self.play_win_sound()
        else:
            self.result_text = self.t('try_again')
        
        if self.balance <5:
            self.result_text = self.t('reset')
            self.draw_game_screen()
            time.sleep(2)
            self.balance = 100
            self.bet_amount =10
            self.result_text = ""
    
    def increase_bet(self):
        if not self.spinning and self.bet_amount < self.balance:
            self.bet_amount = min(self.bet_amount +5, self.balance)
            self.draw_game_screen()
    
    def decrease_bet(self):
        if not self.spinning and self.bet_amount >5:
            self.bet_amount = max(self.bet_amount -5,5)
            self.draw_game_screen()
    
    def show_insufficient_funds(self):
        self.insufficient_funds = True
        self.result_text = self.t('insufficient')
        for _ in range(3):
            self.draw_game_screen()
            time.sleep(0.3)
            self.result_text = ""
            self.draw_game_screen()
            time.sleep(0.3)
        self.insufficient_funds = False
        self.result_text = ""
    
    def cleanup(self):
        mixer.music.stop()
        if self.win_sound:
            self.win_sound.stop()
        mixer.quit()
        self.display.clear()

from key import Button, language
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    button = Button()
    game = None
    try:
        print("Starting fruit slot machine...")
        la = language()  # Get language setting ('cn' or 'en')
        game = FruitSlotMachine(language=la)
        while True:
            if button.press_a():
                game.spin()
            elif button.press_d():
                game.increase_bet()
            elif button.press_c():
                game.decrease_bet()
            elif button.press_b():
                print("Thanks for playing!")
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        if game:
            game.cleanup()
        logging.info("Program exited")