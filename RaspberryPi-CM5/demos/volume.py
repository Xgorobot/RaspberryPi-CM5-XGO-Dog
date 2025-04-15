from uiutils import (
    draw,splash,display,vol_logo,lal,splash_theme_color,color_white,
    color_bg,color_unselect,color_purple,get_font,display_cjk_string,Button
   )

import sys,os


sys.path.append("..")


#Basic initialization
button = Button()
font1 = get_font(16)
font2 = get_font(18)


#LCD display
splash.paste(vol_logo, (133, 25), vol_logo)
text_width = draw.textlength(lal["VOLUME"]["VOLUMe"], font=font2)
title_x = (320 - text_width) / 2

display_cjk_string(
    draw,
    title_x,
    90,
    lal["VOLUME"]["VOLUMe"],
    font_size=font2,
    color=color_white,
    background_color=color_bg,
)
display.ShowImage(splash)

#set volume

def volume_level():
    current_dir = os.getcwd()
    print(current_dir)
    volume_ini_path = os.path.join(current_dir, "volume", "volume.ini")
    print(volume_ini_path)
    with open(volume_ini_path, "r") as f:
        volume = f.read()
        print(f"current volume:{volume}")
    return volume

res =volume_level()
volume = int(res)
select = 0

while 1:
    draw.rectangle([(20, 150), (300, 170)], fill=color_unselect)
    vol_width = 20 + int(280 / 100 * volume)
    draw.rectangle([(20, 150), (vol_width, 170)], fill=color_purple)
    draw.rectangle([(144, 180), (320, 240)], fill=splash_theme_color)
    display_cjk_string(
        draw,
        144,
        180,
        str(volume) + "%",
        font_size=font2,
        color=color_white,
        background_color=color_bg,
    )
    display.ShowImage(splash)
    if button.press_c():
        if volume == 0:
            pass
        else:
            volume -= 5
    elif button.press_d():
        if volume == 100:
            pass
        else:
            volume += 5
    elif button.press_a():
        break
    elif button.press_b():
        os._exit(0)

current_dir = os.getcwd()

volume_ini_path = os.path.join(current_dir, "volume", "volume.ini")

with open(volume_ini_path, "w") as f:
    f.write(str(volume))
    
#Enter command to change volume
oscmd = "pactl set-sink-volume @DEFAULT_SINK@ " + str(volume) + "%"
#print(oscmd)
os.system(oscmd)
text_width = draw.textlength(lal["VOLUME"]["SAVED"], font=font2)
title_x = (320 - text_width) / 2
display_cjk_string(
    draw,
    title_x,
    210,
    lal["VOLUME"]["SAVED"],
    font_size=font2,
    color=color_white,
    background_color=color_bg,
)
display.ShowImage(splash)
