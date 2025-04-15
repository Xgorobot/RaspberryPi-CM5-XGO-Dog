from picamera2 import Picamera2
import pyzbar.pyzbar as pyzbar
import cv2
import time
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from uiutils import display, Button,lal

def draw_chinese_text(img, text, position, font_path="/home/pi/model/msyh.ttc", font_size=24, color=(255, 0, 0)):

    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)


    font = ImageFont.truetype(font_path, font_size)


    draw.text(position, text, font=font, fill=color)


    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
def draw_chinese_text_connect(img, text, position, font_path="/home/pi/model/msyh.ttc", font_size=18, color=(0, 255, 0)):

    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)


    font = ImageFont.truetype(font_path, font_size)


    draw.text(position, text, font=font, fill=color)


    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def create_hotspot(ssid, password):
    cmd = f'pkexec nmcli dev wifi connect "{ssid}" password "{password}"'
    print(f"Executing: {cmd}")
    result = os.system(cmd)
    if result == 0:
        print("Connected successfully")
        return True
    else:
        print(f"Connection failed: {result}")
        return False

def main():
    button = Button()
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
    picam2.start()

    print("QR scanner started...")

    try:
        while True:
            img = picam2.capture_array()
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            barcodes = pyzbar.decode(gray_img)

            if not barcodes:
                print('useless data')
                text = "{}".format(lal['NETWORK']['NOQR'])
                img = draw_chinese_text(img, text, (30, 30))
            else:
                for barcode in barcodes:
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    barcode_data = barcode.data.decode("utf-8")

                    if barcode_data.startswith("WIFI:"):
                        parts = barcode_data[5:].split(";")
                        wifi_config = {}
                        for part in parts:
                            if ":" in part:
                                key, value = part.split(":", 1)
                                wifi_config[key] = value

                        ssid = wifi_config.get("S", "")
                        password = wifi_config.get("P", "")

                        if ssid and password:
                            text = "{}".format(lal['NETWORK']['SUCCESS'])
                            img = draw_chinese_text_connect(img, text, (30, 30))
                            display_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                            display.ShowImage(display_img)
                        
                            time.sleep(0.3)
                        
                            success = create_hotspot(ssid, password)
                        
                            if success:
                                time.sleep(3)
                                return


            display_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            display.ShowImage(display_img)
            time.sleep(0.05)

            if button.press_b():
                print("B button pressed - exiting...")
                break

    except KeyboardInterrupt:
        print("Program stopped by user")
    finally:
        picam2.stop()
        print("Camera released")

if __name__ == "__main__":
    main()
