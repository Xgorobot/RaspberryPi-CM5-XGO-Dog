import RPi.GPIO as GPIO
import time,os
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont
import subprocess
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
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


def load_language():
    current_dir = os.getcwd()
    print(current_dir)
    language_ini_path = os.path.join(current_dir, "language", "language.ini")
    print(language_ini_path)
    with open(language_ini_path, 'r') as f:
        language = f.read().strip()
        print(language)
    language_pack = os.path.join(current_dir, "language", language + ".la")
    print(language_pack)
    with open(language_pack, 'r') as f:
        language_json = f.read()
    cleaned_json = re.sub(r'[\x00-\x1f\x7f]', '', language_json)
    language_dict = json.loads(cleaned_json)
    return language_dict

'''
    Loading Language Information From language.ini
'''
def language():
    current_dir = os.getcwd()
    print(current_dir)
    language_ini_path = os.path.join(current_dir, "language", "language.ini")
    language_ini_path = '/home/pi/RaspberryPi-CM5/language/language.ini'
    print(language_ini_path)
    with open(language_ini_path,'r') as f:
        language=f.read()
        result_la = language.strip()
        print(result_la)
    return result_la


