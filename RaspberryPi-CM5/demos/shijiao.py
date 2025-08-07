from xgolib import XGO
from uiutils import Button,font1,draw,display,splash,la
import time

dog = XGO(port='/dev/ttyAMA0', version="xgolite")
fm = dog.read_firmware()

if fm[0] == 'M':
    print('XGO-MINI')
    dog = XGO(port='/dev/ttyAMA0', version="xgomini")
    dog_type = 'M'
else:
    print('XGO-LITE')
    dog = XGO(port='/dev/ttyAMA0', version="xgolite")
    dog_type = 'L'

button = Button()
dog.load_allmotor() 
dog.attitude('p', 15)
dog.translation('z', 75)

recording = False
action_count = 0

while True:
    if la == "cn":
        content = "右下角进入示教模式\n左上角停止记录并复现"
    else:
        content = "Teaching mode: lower right corner\nStop & replay: upper left corner"
    draw.text((30, 115), content, fill="WHITE", font=font1)
    display.ShowImage(splash)
    if button.press_a() and not recording:  # 右下键进入示教模式
        print("进入示教模式，开始记录舵机角度...")
        dog.unload_motor(5)
        recording = True
        action_count = 0
    
    if recording:
        if button.press_c():  # 按下C键停止记录
            print("停止记录，共记录了", action_count, "个动作")
            recording = False
        else:
            # 持续记录动作
            action_count += 1
            print("记录动作", action_count)
            dog.teach_arm("record", action_count)
            time.sleep(2)  # 等待2秒记录下一个动作
    
    if not recording and button.press_c() and action_count > 0:
        print("开始复现动作...")
        for i in range(action_count):
            print("播放动作", i+1)
            time.sleep(2)
            dog.teach_arm("play", i+1)
    
    if button.press_b():  # 左下键退出程序
        dog.reset()
        break