import os,sys,time,threading,requests
from audio import start_recording, detect_keyword
from language_recognize import test_one

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from uiutils import (
    dog, clear_bottom,clear_top,lcd_draw_string, display, splash, 
    line_break, scroll_text_on_lcd, draw_offline, draw, 
    font2, Button, get_font,la
)

#define base fuctions
font2 = get_font(16)
button=Button()
'''
   Function Name:show_words_Dog
   Function Content:Cue word display 
'''


            
def show_words_dog():
    clear_bottom()
    
    if la == 'cn':
        text_lines = [
            ("跳舞|俯卧撑|撒尿|伸懒腰|祈祷", 170),
            ("向下抓取|波浪|找食物|鸡头", 190),
        ]
    else:
       text_lines = [

            ("let's dance|push up|take a pee", 150),
            ("stretch body|start pray|look for food" , 170),
            ("chicken head| pick up|do wave", 190),

        ]
    
    for text, y in text_lines:
        lcd_draw_string(draw, 10, y, text, color=(0, 255, 255), scale=font2, mono_space=False)
    
    display.ShowImage(splash)




def button_listener():
    while True:
        if button.press_b():
            print("Button B pressed, exiting...")
            os._exit(0) 
        time.sleep(0.1)


#Start button listening thread
button_thread = threading.Thread(target=button_listener)
button_thread.daemon = True  
button_thread.start()

def actions_dog(act):

    command_actions = {
        "cn": {
            "跳舞": 23,
            "俯卧撑": 21,
            "撒尿": 11,
            "伸懒腰": 14,
            "祈祷": 17,
            "找食物": 18,
            "鸡头":20,
            "向下抓取": 130,
            "波浪": 15,"拨浪":15,
        },
        "en": {
             "dance": 23, "let's dance": 23,
             "push up": 21,"push": 21,
             "pee": 11, "take a pee": 11, "take": 11,
             "stretch": 14, "body": 14,"stretch body": 14,
             "pray": 17,"start": 17, "start pray": 17,
             "food": 18,"look": 18, "look for food": 18,
             "head": 20, "chicken": 20,"chicken head": 20,
             "pick": 130, "pick up": 130,
             "wave": 15,"do wave": 15,
        }
    }

    commands = command_actions.get(la, command_actions["en"])

    for cmd, action in commands.items():
        try:
            if cmd.lower() in act:  
                dog.action(action)
                time.sleep(3)
                dog.reset()
                return True 

        except TypeError:
            time.sleep(2)
            return False 


    print("Command not found")
    error_msg = "错误命令词，请再次尝试" if la == "cn" else "Wrong command. Please try again"
    clear_top()
    lcd_draw_string(
        draw, 60, 70, error_msg, color=(255, 0, 0), scale=font2, mono_space=False
    )
    display.ShowImage(splash)
    time.sleep(1)
    dog.reset()
    return False

#Test the network
net = False
try:
    html = requests.get("http://www.baidu.com", timeout=2)
    net = True
except Exception as e:
    print(f"Network check failed: {e}")
    net = False

#Record and control the dog
if net:
    while True:
        show_words_dog()
        if detect_keyword():
            clear_top()
            start_recording()
            content = test_one()

            if content != "":
                clear_top()
                speech_list = line_break(content)
                print(speech_list)
               
                if la == "en":
                    english_only = ''.join(char for char in speech_list if ord(char) < 128)
                    display_text = english_only
                else:
                    display_text = speech_list
                    
                lcd_draw_string(
                    draw,
                    10,
                    110,
                    display_text, 
                    color=(255, 255, 255),
                    scale=font2,
                    mono_space=False,
                )
                display.ShowImage(splash)
                
                lines = len(display_text.split("\n"))  
                tick = 0.3
                if lines > 6:
                    scroll_text_on_lcd(re_e, 10, 111, 6, tick)
                
               
                if not actions_dog(content):
                    continue  

            if content == 0:
               break

        time.sleep(0.1)  
else:
    draw_offline()
    while True:
        time.sleep(0.1)

