from uiutils import (get_font, get_path, display_cjk_string, Button, color_white, color_bg,
                   color_unselect, color_purple, draw, splash, display, lan_logo, arrow_logo_1, lal)
import sys, time, os

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


country_list = [["English", "en"], ["中文", "cn"]]
select = 0

while True:
    # Draw UI
    draw.rectangle([(20, 145), (300, 180)], fill=color_purple)
    if content == "cn":
        draw.rectangle([(160, 146), (299, 179)], fill=color_unselect)
    else:
        draw.rectangle([(21, 146), (160, 179)], fill=color_unselect)
    
    # Display options
    display_cjk_string(draw, 80, 150, "CN", font_size=font2, color=color_white, background_color=color_bg)
    display_cjk_string(draw, 220, 150, "EN", font_size=font2, color=color_white, background_color=color_bg)
    splash.paste(arrow_logo_1, (148, 150), arrow_logo_1)
    display.ShowImage(splash)

    # Button controls
    if button.press_c(): content = "cn"     
    elif button.press_d(): content = "en"   
    elif button.press_a(): break             
    elif button.press_b(): os._exit(0)       

# Save settings
with open(language_ini_path, "w") as f:
    f.write(content)

# Show confirmation
text_width = draw.textlength(lal["LANGUAGE"]["SAVED"], font=font2)
title_x = (320 - text_width) / 2
display_cjk_string(draw, title_x, 200, lal["LANGUAGE"]["SAVED"], font_size=font2, color=color_white, background_color=color_bg)
display.ShowImage(splash)

time.sleep(2)
os.system('sudo reboot')  
