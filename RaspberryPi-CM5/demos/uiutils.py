#../CM5/demos/uitils.py
#demos' basic function package
import RPi.GPIO as GPIO
from xgolib import XGO
import spidev as SPI
import subprocess
import os, socket, sys, time, json,re,random,socket
from PIL import Image, ImageDraw, ImageFont
import xgoscreen.LCD_2inch as LCD_2inch
import random
#set GPIO model
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# define colors
btn_selected = (24, 47, 223)
btn_unselected = (20, 30, 53)
txt_selected = (255, 255, 255)
txt_unselected = (76, 86, 127)
splash_theme_color = (15, 21, 46)
color_black = (0, 0, 0)
color_white = (255, 255, 255)
color_red = (238, 55, 59)
color_purple =(24,27,223)
color_bg = (8, 10, 26)
color_unselect = (89, 99, 149)
color_select = (24, 47, 223)
mic_purple = (24, 47, 223)
# Font Cache
_font_cache = {}

#define logos
pics_dir = "/home/pi/RaspberryPi-CM4/pics"
lan_logo = Image.open(os.path.join(pics_dir, "L@2x.png"))
arrow_logo_1 = Image.open(os.path.join(pics_dir, "C@2x.png"))
vol_logo = Image.open(os.path.join(pics_dir, "s@2x.png"))
wifi_logo = Image.open(os.path.join(pics_dir, "5G@2x.png"))
arrow_logo_2 = Image.open(os.path.join(pics_dir, "J@2x.png"))
fm_logo = Image.open(os.path.join(pics_dir, "F@2x.png"))
py_wave = Image.open(os.path.join(pics_dir, "P@2x.png"))
os_logo = Image.open(os.path.join(pics_dir, "os@2x.png"))
mic_logo = Image.open(os.path.join(pics_dir, "mic.png"))
mic_wave = Image.open(os.path.join(pics_dir, "mic_wave.png"))
offline_logo = Image.open(os.path.join(pics_dir, "offline.png"))
draw_logo = Image.open(os.path.join(pics_dir, "gpt_draw.png"))
fm_logo = Image.open("/home/pi/RaspberryPi-CM4/pics/F@2x.png")
re_logo = Image.open("/home/pi/RaspberryPi-CM4/pics/redian@2x.png")

def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype("/home/pi/model/msyh.ttc", size)
    return _font_cache[size]

# Define Font
font1 = get_font(15)
font2 = get_font(22)
font3 = get_font(30)
font4 = get_font(40)
#display battery in screen
bat = Image.open(os.path.join(pics_dir, "battery.png"))

class Button:
    def __init__(self):
        self.keys = {
            "A": 24,
            "B": 23,
            "C": 17,
            "D": 22
        }
        self.setup_pins()

    def setup_pins(self):
      
        for pin in self.keys.values():
            os.system(f"sudo pinctrl set {pin} ip")

    def read_pin(self, pin):
      
        result = subprocess.run(["sudo", "pinctrl", "level", str(pin)], capture_output=True, text=True).stdout
        return result[0] == "1"

    def press_button(self, key_name):
        
        pin = self.keys.get(key_name)
        if pin is None:
            return False
        
        if self.read_pin(pin):
            return False

        # Wait until the button is released (pin reads '1')
        while not self.read_pin(pin):
            time.sleep(0.01)
        return True

    def press_a(self):
        return self.press_button("A")

    def press_b(self):
        if self.press_button("B"):
            os.system("pkill mplayer")
            return True
        return False

    def press_c(self):
        return self.press_button("C")

    def press_d(self):
        return self.press_button("D")

#tested
'''
    Loading Language Information From language.ini
'''

def get_path(path):
    current_dir = os.getcwd()
    language_ini_path = os.path.join(current_dir, "language", "language.ini")
    if path == "current":
        return current_dir
    elif path == "language_ini_path":
        return language_ini_path
    else:
        raise ValueError("Invalid path type specified")
        
def get_language():
    language_ini_path=get_path("language_ini_path")
    try:
        with open(language_ini_path, 'r') as f:
            language=f.read().strip()
            print(language)
            return language
    except Exception as e:
        print(f"Error reading language.ini: {e}")
        return None


def load_language():
    language=get_language()
    current_dir=get_path("current")
    language_pack = os.path.join(current_dir, "language", language + ".la")
    #print(f"language_pack path is:{language_pack}")
    with open(language_pack, 'r') as f:
        language_json = f.read()
    cleaned_json = re.sub(r'[\x00-\x1f\x7f]', '', language_json)
    language_dict = json.loads(cleaned_json)
    return language_dict

class DogTypeChecker:
    def __init__(self):
        self._dog_type_cache = None
        self._dog_instance_cache = None
        self._is_permissions_set = False
        self.dog = None

    def check_type(self):

        if self._dog_type_cache is not None:
            return self._dog_type_cache


        if not self._is_permissions_set:
            os.system("sudo chmod 777 -R /dev/ttyAMA0")
            self._is_permissions_set = True


        if self.dog is None:
            self.dog = XGO(port="/dev/ttyAMA0", version="xgolite")

        fm = self.dog.read_firmware()

        firmware_mapping = {
            "M": ("M", "MINI", "xgomini"),
            "L": ("L", "LITE", "xgolite"),
            "R": ("R", "RIDER", "xgorider"),
        }

        if fm[0] in firmware_mapping:
            dog_type, firmware_info, version = firmware_mapping[fm[0]]
        else:
            raise ValueError("Unknown firmware type")

        self._dog_type_cache = (dog_type, version, firmware_info)

        return self._dog_type_cache


dog_type_checker = DogTypeChecker()
dog_type, version, firmware_info = dog_type_checker.check_type()
dog = XGO(port="/dev/ttyAMA0", version="xgolite")


display = LCD_2inch.LCD_2inch()
display.Init()
display.clear()
# Init Splash
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)


dog_type,firmware_info,version =dog_type_checker.check_type()

print(version)



def show_battery_template():
    lcd_rect(200, 0, 320, 25, color=splash_theme_color, thickness=-1)
    draw.bitmap((270, 4), bat)


def show_battery():
    show_battery_template()  

    try:
        battery = dog.read_battery()
        print(f"The Battery Level is {battery}")

        if str(battery) == "0":
            print("uart error")
            show_battery_template()   
        else:
            x_offset = 286 - (len(str(battery)) - 1) * 6
            lcd_draw_string(draw, x_offset, 4, str(battery), color=color_white, scale=font1)
    except Exception as e:
        print("uart error:", e)
        
la = get_language()
lal=load_language()
def display_cjk_string(
    splash,
    x,
    y,
    text,
    color=(255, 255, 255),
    font_size=1,
    scale=1,
    mono_space=False,
    auto_wrap=True,
    background_color=(0, 0, 0),
    ):
    splash.text((x, y), text, fill=color, font=font_size)

#draw methods

def show_button_template(left, right, text1, text2, text3):
    lcd_rect(0, 188, 320, 240, color=btn_unselected, thickness=-1)  
    lcd_rect(left, 188, right, 240, color=btn_selected, thickness=-1)  
    lcd_draw_string(draw, 7, 195, lal["MAIN"][text1], color=color_white, scale=font2)
    lcd_draw_string(draw, 110, 195, lal["MAIN"][text2], color=color_white, scale=font2)
    lcd_draw_string(draw, 215, 195, lal["MAIN"][text3], color=color_white, scale=font2)
    draw.line((110, 188, 110, 240), fill=txt_unselected, width=1,joint=None)
    draw.line((210, 188, 210, 240), fill=txt_unselected, width=1,joint=None)
    draw.rectangle((0, 188, 320, 240), outline=txt_unselected, width=1)

                                                           
def show_button(left1,right1,left2,text):
    lcd_rect(left1, 188, right1, 240, color=btn_selected, thickness=-1)
    lcd_draw_string(draw, left2, 195, lal["MAIN"][text], color=color_white, scale=font2)
    
#draw
def lcd_draw_string(
    splash,
    x,
    y,
    text,
    color=(255, 255, 255),
    font_size=1,
    scale=1,
    mono_space=False,
    auto_wrap=True,
    background_color=(0, 0, 0),
):
    splash.text((x, y), text, fill=color, font=scale)

def lcd_rect(x, y, w, h, color, thickness):
    draw.rectangle([(x, y), (w, h)], fill=color, width=thickness)
    
def lcd_draw_string(splash, x, y, text, color=(255, 255, 255), font_size=1, scale=1, mono_space=False, auto_wrap=True, background_color=(0, 0, 0)):
    splash.text((x, y), text, fill=color, font=scale)

def lcd_rect(x, y, w, h, color, thickness):
    draw.rectangle([(x, y), (w, h)], fill=color, width=thickness)

def draw_wave(ch):
    def draw_wave_section(start_x, start_y):
        width, height = 80, 50
        y_center = height // 2
        current_y = y_center
        previous_point = (start_x, y_center + start_y)
        draw.rectangle([(start_x - 1, start_y), (start_x + width, start_y + height)], fill=splash_theme_color)

        x = 0
        while x < width:
            segment_length = random.randint(7, 25)
            gap_length = random.randint(4, 20)

            for _ in range(segment_length):
                if x >= width: break
                current_y += ch
                current_y = max(0, min(current_y, height - 1))
                current_point = (x + start_x, current_y + start_y)
                draw.line([previous_point, current_point], fill="white")
                previous_point = current_point
                x += 1

            for _ in range(gap_length):
                if x >= width: break
                current_point = (x + start_x, y_center + start_y)
                draw.line([previous_point, current_point], fill="white", width=2)
                previous_point = current_point
                x += 1

    draw_wave_section(40, 42)
    draw_wave_section(210, 42)

def draw_cir(ch):
    draw.rectangle([(55, 40), (120, 100)], fill=splash_theme_color)
    draw.rectangle([(205, 40), (270, 100)], fill=splash_theme_color)
    radius = 4
    cy = 70
    centers = [(62, cy), (87, cy), (112, cy), (210, cy), (235, cy), (260, cy)]

    for center in centers:
        random_offset = ch
        new_y = center[1] + random_offset
        new_y2 = center[1] - random_offset
        draw.line([center[0], new_y2, center[0], new_y], fill="white", width=11)

        for new_y_val in [new_y, new_y2]:
            top_left = (center[0] - radius, new_y_val - radius)
            bottom_right = (center[0] + radius, new_y_val + radius)
            draw.ellipse([top_left, bottom_right], fill="white")

def clear_bottom():
    draw.rectangle([(0, 111), (320, 240)], fill=splash_theme_color)
    
def line_break(line):
    if not line:
        if la=='cn':
          return "我没有听见声音欸，再呼唤我一次吧!"
        else:
          return "No sound? Call me Lulu again"
    LINE_CHAR_COUNT = 19 * 2
    CHAR_SIZE = 20
    TABLE_WIDTH = 4
    ret = ""
    width = 0
    for c in line:
        if len(c.encode("utf8")) == 3:
            if LINE_CHAR_COUNT == width + 1:
                width = 2
                ret += "\n" + c
            else:
                width += 2
                ret += c
        else:
            if c == "\t":
                space_c = TABLE_WIDTH - width % TABLE_WIDTH
                ret += " " * space_c
                width += space_c
            elif c == "\n":
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= LINE_CHAR_COUNT:
            ret += "\n"
            width = 0
    if ret.endswith("\n"):
        return ret
    return ret + "\n"
    
def scroll_text_on_lcd(text, x, y, max_lines, delay):
    lines = text.split("\n")
    total_lines = len(lines)
    
    for i in range(total_lines - max_lines + 1):
        lcd_rect(0, 110, 320, 240, splash_theme_color, -1)
        visible_lines = lines[i:i + max_lines]
        
        for j, line in enumerate(visible_lines):
            lcd_draw_string(
                draw,
                x,
                y + j * 20,
                line,
                color=(255, 255, 255),
                scale=font2,
                mono_space=False,
            )
        
        display.ShowImage(splash)
        time.sleep(delay)
        
def draw_offline():
    draw.bitmap((115, 20), offline_logo, "red")
    warn_text = "Wifi unconnected"
    draw.text((90, 140), warn_text, fill=(255, 255, 255), font=font3)
    display.ShowImage(splash)
    
def clear_top():
    draw.rectangle([(0, 0), (320, 111)], fill=splash_theme_color)



