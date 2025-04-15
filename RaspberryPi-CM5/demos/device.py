import sys,time,os 
from uiutils import (
    splash_theme_color, dog,draw,splash,font1,font2,display,
    fm_logo,py_wave,os_logo,lal,Button
)

sys.path.append("..")

#Init Key
button = Button()

#LCD display Text
def lcd_text(x, y, content):
    draw.text((x, y), content, fill="WHITE", font=font1)
    display.ShowImage(splash)


def lcd_text_title(x, y, content):
    draw.text((x, y), content, fill="WHITE", font=font2)
    display.ShowImage(splash)

#Version Information
fm1 = dog.read_firmware()
fm2 = dog.read_lib_version()
fm3 = "V3"

#Visualization
draw.rectangle([(20, 90), (100, 210)], fill=splash_theme_color)
draw.rectangle([(120, 90), (200, 210)], fill=splash_theme_color)
draw.rectangle([(220, 90), (300, 210)], fill=splash_theme_color)

splash.paste(fm_logo, (50, 70), fm_logo)
splash.paste(py_wave, (140, 70), py_wave)
splash.paste(os_logo, (240, 70), os_logo)

text_width = draw.textlength(lal["DEVICE"]["DEVICEINFO"], font=font2)
title_x = (320 - text_width) / 2
lcd_text_title(title_x, 20, lal["DEVICE"]["DEVICEINFO"])
lcd_text(35, 115, "Firmware")
lcd_text_title(36, 160, fm1)
lcd_text(133, 115, "Python")
lcd_text_title(135, 160, fm2)
lcd_text(250, 115, "OS")
lcd_text_title(250, 160, fm3)

while True:
    time.sleep(0.01)
    
    if button.press_b():
        os._exit(0)
