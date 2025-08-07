from rtmpose_processor import RTMPoseProcessor
from exercise_counters import ExerciseCounter
# 只使用CPU设备
device = 'cpu'

# 设置默认模型模式
model_mode = 'lightweight'

# 创建运动计数器实例
exercise_counter = ExerciseCounter()
pose_processor = RTMPoseProcessor(
            exercise_counter=exercise_counter,
            mode=model_mode,
            backend='onnxruntime',
            device=device
        )

'''
squat 深蹲
pushup 俯卧撑
situp 仰卧起坐
bicep_curl 二头肌弯举
lateral_raise	侧平举
overhead_press	头顶推举
leg_raise	抬腿
knee_raise	提膝
left_knee_press	左膝下压
right_knee_press	右膝下压
'''
action_dic={'squat':'深蹲',
            'pushup':'俯卧撑',
            'situp':'仰卧起坐',
            'bicep_curl':'二头肌弯举',
            'lateral_raise':'侧平举',
            'overhead_press':'头顶推举',
            'leg_raise':'抬腿',
            'knee_raise':'提膝',
            'left_knee_press':'左膝下压',
            'right_knee_press':'右膝下压'
            }
action_list = ['squat','pushup','situp','bicep_curl','lateral_raise','overhead_press','leg_raise','knee_raise','left_knee_press','right_knee_press']
from PIL import Image, ImageDraw, ImageFont
from key import Button,language
import xgoscreen.LCD_2inch as LCD_2inch
la=language()
button = Button()
splash_theme_color = (0,0,0)
display = LCD_2inch.LCD_2inch()
display.Init()
display.clear()
# Init Splash
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

def lcd_draw_string(
    draw,  # 修改为直接使用draw对象
    x,
    y,
    text,
    color=(255, 255, 255),
    font_size=16,
    max_width=340,
    max_lines=5,
    clear_area=False
):
    font = ImageFont.truetype("/home/pi/model/msyh.ttc", font_size)
    line_height = font_size + 2
    total_height = max_lines * line_height
    
    if clear_area:
        draw.rectangle((x, y, x + max_width, y + total_height), fill=(15, 21, 46))
    
    lines = []
    current_line = ""
    
    # 处理文本中的换行符
    paragraphs = text.split('\n')
    
    for para in paragraphs:
        words = []
        # 将中英文组合拆分为可分割的单元
        temp_word = ""
        for char in para:
            # 判断是否为ASCII字符(英文)
            if ord(char) < 256:
                if temp_word and not temp_word.isascii():
                    words.append(temp_word)
                    temp_word = ""
                temp_word += char
            else:
                if temp_word and temp_word.isascii():
                    words.append(temp_word)
                    temp_word = ""
                temp_word += char
        if temp_word:
            words.append(temp_word)
        
        current_line = ""
        for word in words:
            # 测试添加这个词是否会超出宽度
            test_line = current_line + word
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:  # 如果当前行有内容，先保存
                    lines.append(current_line)
                # 处理一个词就超长的情况
                if font.getlength(word) > max_width:
                    # 对超长英文单词进行分割
                    if word.isascii():
                        split_pos = 0
                        while split_pos < len(word):
                            remaining = len(word) - split_pos
                            # 找最大能显示的长度
                            for l in range(remaining, 0, -1):
                                if font.getlength(word[split_pos:split_pos+l]) <= max_width:
                                    lines.append(word[split_pos:split_pos+l])
                                    split_pos += l
                                    break
                    else:  # 中文超长，按字符分割
                        for char in word:
                            lines.append(char)
                    current_line = ""
                else:
                    current_line = word
        if current_line:
            lines.append(current_line)
    
    # 限制最大行数
    if max_lines:
        lines = lines[:max_lines]
    
    # 绘制文本
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, fill=color, font=font)
   
   
i = 0   
while True:

    exercise_type = action_list[i]
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    #Show Wake Up Call
    if la=="cn":
        text1=f"当前检测的运动为\n{action_dic[exercise_type]}({exercise_type})"
    else:
        text1=f"The current detected motion is\n{exercise_type}"
              
    lcd_draw_string(
        draw,
        x=50,
        y=60,
        text=text1,
        color=(255, 255, 255),
        font_size=26,
        max_width=240,
        max_lines=5,
        clear_area=False
    )
    display.ShowImage(splash)
    if button.press_d():
        i += 1
        if i >= len(action_list):  
            i = 0
        exercise_type = action_list[i]
    if button.press_c():
        break
    if button.press_b():
        exit()
   

from key import Button,language
import cv2
button = Button()
la=language()
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
picam2.start()
print("摄像头初始化完毕")
# 替换这部分代码：
font = cv2.FONT_HERSHEY_SIMPLEX

# 改为使用PIL绘制中文，再转为OpenCV格式：
from PIL import ImageFont, ImageDraw, Image
import numpy as np

# 在循环前定义中文字体
font_path = "/home/pi/model/msyh.ttc"  # 确保这个路径是正确的
font_size = 20
pil_font = ImageFont.truetype(font_path, font_size)

while True:
    frame = picam2.capture_array()
    processed_frame, current_angle, keypoints = pose_processor.process_frame(frame, exercise_type)
    
    # 将OpenCV图像转为PIL图像
    pil_img = Image.fromarray(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # 组合显示文本
    if la == "cn":
        display_text = f"{action_dic[exercise_type]}({exercise_type})"  # 中文显示
    else:
        display_text = f"{exercise_type}"  # 英文显示
        
    current_count = exercise_counter.counter
    
    # 计算文本位置
    text_width = draw.textlength(display_text, font=pil_font)
    count_width = draw.textlength(str(current_count), font=pil_font)
    right_margin = 5
    text_x = processed_frame.shape[1] - text_width - right_margin
    count_x = processed_frame.shape[1] - count_width - right_margin
    
    # 绘制文本
    draw.text((text_x, 30), display_text, font=pil_font, fill=(0, 255, 0))
    draw.text((count_x, 60), str(current_count), font=pil_font, fill=(0, 255, 0))
    
    # 转换回OpenCV格式
    processed_frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # 显示图像
    imgok = Image.fromarray(processed_frame)
    display.ShowImage(imgok)
    
    if button.press_b():
        break