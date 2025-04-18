from numpy.f2py.crackfortran import previous_context
from uiutils import (get_font, get_path, display_cjk_string, Button, color_white, color_bg,
                    color_unselect, color_purple, draw, splash, display, lan_logo, arrow_logo_1, lal)
from uiutils import load_language
import sys, time, os
#import subprocess
#import psutil  

# Setup
sys.path.append("..")
button = Button()

font1 = get_font(16)
font2 = get_font(18)

language_ini_path = get_path("language_ini_path")

# Read current language
with open(language_ini_path, "r") as f:
    content = f.read()

# UI setup
splash.paste(lan_logo, (133, 25), lan_logo)
text_width = draw.textlength(lal["LANGUAGE"]["SET"], font=font2)
title_x = (320 - text_width) / 2
display_cjk_string(draw, title_x, 90, lal["LANGUAGE"]["SET"], font_size=font2, color=color_white, background_color=color_bg)
display.ShowImage(splash)

def update_ui():
    splash.paste(lan_logo, (133, 25), lan_logo)
    text_width = draw.textlength(lal["LANGUAGE"]["SET"], font=font2)
    title_x = (320 - text_width) / 2
    display_cjk_string(draw, title_x, 90, lal["LANGUAGE"]["SET"], font_size=font2, color=color_white,
                      background_color=color_bg)

    draw.rectangle([(20, 145), (300, 180)], fill=color_purple)
    if content == "cn":
        draw.rectangle([(160, 146), (299, 179)], fill=color_unselect)
    else:
        draw.rectangle([(21, 146), (160, 179)], fill=color_unselect)

    display_cjk_string(draw, 80, 150, "CN", font_size=font2, color=color_white, background_color=color_bg)
    display_cjk_string(draw, 220, 150, "EN", font_size=font2, color=color_white, background_color=color_bg)
    splash.paste(arrow_logo_1, (148, 150), arrow_logo_1)
    display.ShowImage(splash)


import os

def restart_application():
    print(111)
    with open(language_ini_path, "w") as f:
        f.write(content)
        f.flush()

    print(222)
    text_width = draw.textlength(lal["LANGUAGE"]["SAVED"], font=font2)
    title_x = (320 - text_width) / 2
    display_cjk_string(draw, title_x, 200, lal["LANGUAGE"]["SAVED"], font_size=font2, color=color_white, background_color=color_bg)
    display.ShowImage(splash)
    time.sleep(2)


    os.system("python /home/pi/RaspberryPi-CM4/kill.py")
    os._exit(0)  
    
while True:
    previous_content = content
    
    update_ui()

    if button.press_c(): 
        content = "cn"
    elif button.press_d(): 
        content = "en"
    elif button.press_b(): 
        break  
    elif button.press_a():
        restart_application()  

    if content != previous_content and button.press_a():
        with open(language_ini_path, "w") as f:
            f.write(content)
            lal = load_language()
