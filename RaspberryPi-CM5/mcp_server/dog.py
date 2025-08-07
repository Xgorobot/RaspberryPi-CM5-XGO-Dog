# server.py
from mcp.server.fastmcp import FastMCP
import sys
import logging

logger = logging.getLogger('Calculator')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

import math
import random

# Create an MCP server
mcp = FastMCP("Calculator")

# Add an addition tool

import cv2
import threading
import time
from queue import Queue
from xgolib import XGO
dog = XGO(port='/dev/ttyAMA0', version="xgolite")
@mcp.tool()
def forward(speed:int, speed_time:int) -> dict:
    """time and speed of the dog forwards,The time should be less than ten seconds."""
    dog.move_x(speed)
    time.sleep(speed_time)
    dog.stop()
    return {"success": True, "message": "Dog moved forward"}
@mcp.tool()
def backward(speed:int, speed_time:int) -> dict:
    """time and speed of the dog backwards,The time should be less than ten seconds."""
    dog.move_x(-speed)
    time.sleep(speed_time)
    dog.stop()
    return {"success": True, "message": "Dog moved backward"}
@mcp.tool()
def move_left(speed:int, speed_time:int) -> dict:
    """time and speed of the dog moves left,The time should be less than ten seconds."""
    dog.move('y', speed)
    time.sleep(speed_time)
    dog.stop()
    return {"success": True, "message": "Dog moved left"}
@mcp.tool()
def move_right(speed:int, speed_time:int) -> dict:   
    """time and speed of the dog moves right,The time should be less than ten seconds."""
    dog.move('y', -speed)
    time.sleep(speed_time)
    dog.stop()
    return {"success": True, "message": "Dog moved right"}
@mcp.tool()
def turn_left(speed:int, speed_time:int) -> dict:
    """time and speed of the dog turns left,The time should be less than ten seconds."""
    dog.turn(speed)
    time.sleep(speed_time)
    dog.stop()
    return {"success": True, "message": "Dog turned left"}
@mcp.tool()
def turn_right(speed:int, speed_time:int) -> dict:   
    """time and speed of the dog turns right,The time should be less than ten seconds."""
    dog.turn(-speed)
    time.sleep(speed_time)
    dog.stop()
    return {"success": True, "message": "Dog turned right"}
@mcp.tool()
def stop() -> dict:
    """Stop the dog."""
    dog.stop()
    return {"success": True, "message": "Dog stopped"}
@mcp.tool()
def set_pace_mode(mode: str) -> dict:
    """Set the pace mode of the dog, which can be 'normal', 'high', or 'slow'."""
    # Here you would implement the logic to set the pace mode
    # For example, you might adjust speed parameters based on the mode
    # dog.set_pace_mode(mode)
    if mode not in ['normal', 'high', 'slow']:
        return {"success": False, "message": "Invalid pace mode"}
    else:
        dog.pace(mode)
        return {"success": True, "message": f"Pace mode set to {mode}"}
@mcp.tool()
def set_claw(number: int) -> dict:
    """Set the claw of the dog to a specific number,0 means the jaw is fully open, and 255 means the jaw is completely closed""" 
    dog.claw(number)
    return {"success": True, "message": f"Claw set to {number}"}
# @mcp.tool()
# def set_action(action: str) -> dict:
#     """机械狗的预设动作，有以下选择趴下,站起,转圈,匍匐前进,原地踏步,蹲起,沿x转动,沿y转动,沿z转动,三轴转动,撒尿,坐下,招手，伸懒腰,波浪运动,摇摆运动,求食,找食物,握手,展示机械臂,俯卧撑，张望，跳舞，调皮,机械臂上抓,机械臂中抓,机械臂下抓."""
#     if action not in ['趴下', '站起', '转圈', '匍匐前进', '原地踏步', '蹲起', '沿x转动', '沿y转动', '沿z转动',
#                       '三轴转动', '撒尿', '坐下', '招手', '伸懒腰', '波浪运动', '摇摆运动', '求食', '找食物', '握手',
#                       '展示机械臂', '俯卧撑', '张望', '跳舞', '调皮', '机械臂上抓', '机械臂中抓', '机械臂下抓']:
#           return {"success": False, "message": "Invalid action"}
#     else:
#         action_dict = {
#             '趴下': 1,
#             '站起': 2,
#             '转圈': 3,
#             '匍匐前进': 4,
#             '原地踏步': 5,
#             '蹲起': 6,
#             '沿x转动': 7,
#             '沿y转动': 8,
#             '沿z转动': 9,
#             '三轴转动': 10,
#             '撒尿': 11,
#             '坐下': 12,
#             '招手': 13,
#             '伸懒腰': 14,
#             '波浪运动': 15,
#             '摇摆运动': 16,
#             '求食': 17,
#             '找食物': 18,
#             '握手': 19,
#             '展示机械臂': 20,
#             '俯卧撑': 21,
#             '张望': 22,
#             '跳舞': 23,
#             '调皮': 24,
#             '机械臂上抓': 128,
#             '机械臂中抓': 129,
#             '机械臂下抓': 130

#         }
#         time_list = [0] * 131  
#         time_list[1:25] = [3.5, 3.5, 5.5, 5.5, 4.5, 4.5, 4.5, 4.5, 4.5, 7.5, 7.5, 5.5, 7.5, 10.5, 6.5, 6.5, 6.5, 6.5, 10.5, 9.5, 8.5, 8.5, 6.5, 7.5]
#         time_list[128:131] = [10.5, 10.5, 10.5]
#         action_id = action_dict[action]
#         dog.action(action_id)
#         if time_list[action_id] >= 10:
#             time_list[action_id] = 9.5
#         time.sleep(time_list[action_id])
#         dog.stop()
#         return {"success": True, "message": f"Action set to {action}"}
@mcp.tool()
def set_gait(gait: str) -> dict:
    """Set the gait of the dog, which can be 'trot', 'walk', or 'high_walk', 'slow_trot'.其中trot是默认步态，表示小跑，walk是行走步态，high_walk是高抬腿行走，slow_trot是慢步态，一般用于微调。"""
    if gait not in ['trot', 'walk', 'high_walk', 'slow_trot']:
        return {"success": False, "message": "Invalid gait"}
    else:
        # Here you would implement the logic to set the gait
        # For example, you might adjust speed parameters based on the gait
        dog.gait_type(gait)
        return {"success": True, "message": f"Gait set to {gait}"}
@mcp.tool()
def set_perform(mode: str) -> dict:
    """是否打开表演模式，'True' or 'False'."""
    if mode not in ['True', 'False']:
        return {"success": False, "message": "Invalid perform mode"}
    else:
        # Here you would implement the logic to set the perform mode
        # For example, you might adjust speed parameters based on the mode
        if mode == 'False':
            dog.perform(0)
        else:
            dog.perform(1)
        return {"success": True, "message": f"Perform haven been successed"}
@mcp.tool()
def set_attitude(r:int, p:int ,y:int) -> dict:
    """调整机械狗的角度,沿r轴正时针旋转为正数，0表示回到初始位置，沿着r逆时针旋转为负数，是机械狗机身的滚转角取值范围是[-20,20]；p轴是俯仰角，取值范围是[-15，15]；y轴是偏航角，取值范围是[-11，11]。."""
    if attitude not in ['happy', 'sad', 'angry']:
        return {"success": False, "message": "Invalid attitude"}
    else:
        # Here you would implement the logic to set the attitude
        # For example, you might adjust speed parameters based on the attitude
        dog.attitude(['r', 'p', 'y'],[r,p,y])
        return {"success": True, "message": f"Attitude set to {attitude}"}
@mcp.tool()
def set_translation(x:int, y:int, z:int) -> dict:
    """机械狗的机身平移,data的单位是毫米，沿X轴正方向平移为正数，0表示回到初始位置，沿着X负方向平移为负数，取值范围是[-35,35]，x轴是控制机身前后移动的；y轴的取值范围是[-18,18]，y轴是控制机身左右平移；z轴的取值范围是[75,115]，z轴是控制机身上下平移，也就是机械狗的身高。"""
    if x < -35 or x > 35 or y < -18 or y > 18 or z < 75 or z > 115:
        return {"success": False, "message": "Invalid translation position"}
    else:
        dog.translation(['x', 'y', 'z'],[x, y, z])
        return {"success": True, "message": f"Translation position set to x: {x}, y: {y}, z: {z}"}
@mcp.tool()
def set_arm(x:int,z:int)    -> dict:
    """调整机械狗的机械臂位置,x是机械狗的机械臂相对于机械臂的基座的x坐标(-80和155之间的数组)单位mm,机械狗的机械臂相对于机械臂的基座的z坐标(-95和155之间的数组)单位mm.默认位置为0，0"""
    if x < -80 or x > 155 or z < -95 or z >155:
        return {"success": False, "message": "Invalid arm position"}
    elif x == 0 and z == 0:
        dog.reset()
        return {"success": True, "message": "Arm position reset to initial state"}
    else:
        # Here you would implement the logic to set the arm position
        # For example, you might adjust speed parameters based on the arm position
        dog.arm(x, z)
        return {"success": True, "message": f"Arm position set to x: {x}, z: {z}"}
@mcp.tool()
def leg_1(x:int, y:int, z:int) -> dict:
    """调整机械狗左前腿末端的位置,x是机械狗的前左腿末端的x坐标(-35和35之间的数组)单位mm,y是机械狗的前左腿末端的y坐标(-18和18之间的数组)单位mm,z是机械狗的前左腿末端的z坐标(75和155之间的数组)单位mm.其中x为正时，机械狗的足端位置向前移动，y为正时，足端位置向左移动,z的初始取值为90，取值越大，足端位置越靠上。"""
    if x < -35 or x > 35 or y < -18 or y > 18 or z < 75 or z > 155:
        return {"success": False, "message": "Invalid leg position"}
    else:
        # Here you would implement the logic to set the leg position
        # For example, you might adjust speed parameters based on the leg position
        dog.leg(1,[x, y, z])
        return {"success": True, "message": f"Leg 1 position set to x: {x}, y: {y}, z: {z}"}
@mcp.tool()
def leg_2(x:int, y:int, z:int) -> dict:
    """调整机械狗右前腿末端的位置,x是机械狗的前右腿末端的x坐标(-35和35之间的数组)单位mm,y是机械狗的前右腿末端的y坐标(-18和18之间的数组)单位mm,z是机械狗的前右腿末端的z坐标(75和155之间的数组)单位mm.其中x为正时，机械狗的足端位置向前移动，y为正时，足端位置向左移动,z的初始取值为90，取值越大，足端位置越靠上。"""
    if x < -35 or x > 35 or y < -18 or y > 18 or z < 75 or z > 155:
        return {"success": False, "message": "Invalid leg position"}
    else:
        # Here you would implement the logic to set the leg position
        # For example, you might adjust speed parameters based on the leg position
        dog.leg(2,[x, y, z])
        return {"success": True, "message": f"Leg 2 position set to x: {x}, y: {y}, z: {z}"}
@mcp.tool()
def leg_3(x:int, y:int, z:int) -> dict:
    """调整机械狗右后腿末端的位置,x是机械狗的后右腿末端的x坐标(-35和35之间的数组)单位mm,y是机械狗的后右腿末端的y坐标(-18和18之间的数组)单位mm,z是机械狗的后右腿末端的z坐标(75和155之间的数组)单位mm.其中x为正时，机械狗的足端位置向前移动，y为正时，足端位置向左移动,z的初始取值为90，取值越大，足端位置越靠上。"""
    if x < -35 or x > 35 or y < -18 or y > 18 or z < 75 or z > 155:
        return {"success": False, "message": "Invalid leg position"}
    else:
        # Here you would implement the logic to set the leg position
        # For example, you might adjust speed parameters based on the leg position
        dog.leg(3,[x, y, z])
        return {"success": True, "message": f"Leg 3 position set to x: {x}, y: {y}, z: {z}"}
@mcp.tool()
def leg_4(x:int, y:int, z:int) -> dict:
    """调整机械狗左后腿末端的位置,x是机械狗的后左腿末端的x坐标(-35和35之间的数组)单位mm,y是机械狗的后左腿末端的y坐标(-18和18之间的数组)单位mm,z是机械狗的后左腿末端的z坐标(75和155之间的数组)单位mm.其中x为正时，机械狗的足端位置向前移动，y为正时，足端位置向左移动,z的初始取值为90，取值越大，足端位置越靠上。"""
    if x < -35 or x > 35 or y < -18 or y > 18 or z < 75 or z > 155:
        return {"success": False, "message": "Invalid leg position"}
    else:
        # Here you would implement the logic to set the leg position
        # For example, you might adjust speed parameters based on the leg position
        dog.leg(4,[x, y, z])
        return {"success": True, "message": f"Leg 4 position set to x: {x}, y: {y}, z: {z}"}
@mcp.tool()
def leg_motor(id:int, data:int) -> dict:
    """id是机械狗的电机编号,11是左前腿下面的舵机,12是左前腿中间的舵机,13是左前腿上面的舵机,21是右前腿下面的舵机,22是右前腿中间的舵机,
    23是右前腿上面的舵机,31是右后腿下面的舵机,32是右后腿中间的舵机,33是右后腿上面的舵机,41是左后腿下面的舵机,42是左后腿中间的舵机,43是左后腿上面的舵机.
    data是舵机角度,下面的舵机取值范围是[-73,57],中间的舵机取值范围是[-66,93],上面的舵机取值范围是[-31,31].腿下面舵机的取值范围[-70, 50]，是指小腿顺时针旋转或者逆时针旋转；腿中间舵机的取值范围[-66, 93]，是指大腿顺时针旋转或者逆时针旋转；腿上面舵机的取值范围是[-31, 31]取值为正是，机械狗的大腿会向外伸展"""
    if id not in [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]:
        return {"success": False, "message": "Invalid motor id"}
    if id in [11, 21, 31]:
        if data < -73 or data > 57:
            return {"success": False, "message": "Invalid motor angle"}
    elif id in [12, 22, 32]:
        if data < -66 or data > 93:
            return {"success": False, "message": "Invalid motor angle"}
    elif id in [13, 23, 33]:
        if data < -31 or data > 31:
            return {"success": False, "message": "Invalid motor angle"}
    elif id in [41, 42, 43]:
        if data < -73 or data > 57:
            return {"success": False, "message": "Invalid motor angle"}
    dog.motor(id,data)
    return {"success": True, "message": f"Leg motor {id} set to {data}"}
@mcp.tool()
def claw_motor(id:int , data:int) -> dict:
    """id是机械狗的爪子电机编号,51夹爪的舵机角度[-65,65],52是机械臂小臂的舵机角度[-85,50],53是机械臂大臂的舵机角度[-75,90].51号舵机的取值范围是[-65, 65]，取值为正时，夹爪会收紧；52号舵机的取值范围是[-115, 70]，初始为70，此时大臂和小臂紧紧贴合，取值越小，大臂和小臂的角度越大；53号舵机的取值范围是[-85, 100]初始为-85，此时大臂和机身紧紧贴合，取值越大，大臂和机身的角度越大"""
    if id not in [51, 52, 53]:
        return {"success": False, "message": "Invalid claw motor id"}
    if id == 51:
        if data < -65 or data > 65:
            return {"success": False, "message": "Invalid claw motor angle"}
    elif id == 52:                                      
        if data < -85 or data > 50:
            return {"success": False, "message": "Invalid claw motor angle"}
    elif id == 53:
        if data < -75 or data > 90:
            return {"success": False, "message": "Invalid claw motor angle"}
    dog.motor(id, data)
    return {"success": True, "message": f"Claw motor {id} set to {data}"}
@mcp.tool()
def dog_reset() -> dict:
    """Reset the dog to its initial state."""
    # Here you would implement the logic to reset the dog
    # For example, you might stop all movements and reset positions
    dog.reset()
    return {"success": True, "message": "Dog has been reset to initial state"}
# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
