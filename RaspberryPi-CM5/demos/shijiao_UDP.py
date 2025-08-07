from xgolib import XGO
from uiutils import Button, font1, draw, display, splash,la
import time
import socket
import json
import sys
import select  # 添加缺失的select模块导入

# 初始化
dog = XGO(port='/dev/ttyAMA0', version="xgomini")
button = Button()
dog.attitude('p', 15)
dog.translation('z', 75)

# 网络设置
UDP_IP = "255.255.255.255"  # 广播地址
UDP_PORT = 5005
UDP_TIMEOUT = 0.1  # 缩短超时时间，提高响应速度

def send_arm_angles(angles):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(UDP_TIMEOUT)
        data = json.dumps({"arm_angles": angles}).encode('utf-8')
        sock.sendto(data, (UDP_IP, UDP_PORT))
        print(f"[Host] Sent angles: {angles}")
    except Exception as e:
        print(f"[Host] Send failed: {e}")
    finally:
        if 'sock' in locals():
            sock.close()
            
def receive_arm_angles():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(UDP_TIMEOUT)  # 使用设定的超时时间
        sock.bind(('0.0.0.0', UDP_PORT))  # 明确绑定所有接口
        
        data, addr = sock.recvfrom(1024)
        print(f"[从机] 收到原始数据: {data}")  # 调试打印
        try:
            data = json.loads(data.decode('utf-8'))
            if "arm_angles" in data:
                print(f"[从机] 成功解析角度: {data['arm_angles']} (来自 {addr[0]})")
                return data["arm_angles"], "success"
            else:
                print("[从机] 数据中缺少arm_angles字段")
                return None, "invalid_data"
        except json.JSONDecodeError as e:
            print(f"[从机] JSON解析错误: {e}")
            return None, "json_error"
    except socket.timeout:
        print("[从机] 接收超时 (正常现象)")
        return None, "timeout"
    except Exception as e:
        print(f"[从机] 接收异常: {e}")
        return None, "error"
    finally:
        if 'sock' in locals():
            sock.close()


def check_exit_buttons():
    """检查退出按钮（B强制退出，C返回）"""
    if button.press_b():
        dog.reset()
        sys.exit(0)
    if button.press_c():
        return True
    return False

def host_mode():
    """主机模式"""
    dog.unload_motor(5)
    while True:
        # 显示界面
        draw.rectangle((0, 0, display.height, display.width), fill="BLACK")
        if la == "cn":
            draw.text((20, 80), "主机模式运行中", fill="CYAN", font=font1)
            draw.text((20, 120), "C:返回  B:强制退出", fill="WHITE", font=font1)
        else:
            draw.text((20, 80), "Host Mode Running", fill="CYAN", font=font1)
            draw.text((20, 120), "C:Back  B:Force Exit", fill="WHITE", font=font1)
        display.ShowImage(splash)
        
        # 业务逻辑
        motor_data = dog.read_motor()
        if motor_data:
            send_arm_angles(motor_data[-3:])
        
        # 按钮检测
        if check_exit_buttons():
            break
            
        time.sleep(0.1)

def client_mode():
    """从机模式"""
    dog.load_allmotor()
    while True:
        # 显示界面
        draw.rectangle((0, 0, display.height, display.width), fill="BLACK")
        if la == "cn":
            draw.text((20, 80), "从机模式运行中", fill="CYAN", font=font1)
            draw.text((20, 120), "C:返回  B:强制退出", fill="WHITE", font=font1)
        else:
            draw.text((20, 80), "Client Mode Running", fill="CYAN", font=font1)
            draw.text((20, 120), "C:Back  B:Force Exit", fill="WHITE", font=font1)
        display.ShowImage(splash)
        
        # 业务逻辑（非阻塞）
        angles, status = receive_arm_angles()
        if status == "success":
            dog.motor([51, 52, 53], angles)
        
        # 按钮检测（优先处理）
        if check_exit_buttons():
            break
            
        time.sleep(0.1)

# 主循环
while True:
    # 主菜单界面
    draw.rectangle((0, 0, display.height, display.width), fill="BLACK")
    if la == "cn":
        draw.text((35, 80), "A:主机模式  D:从机模式", fill="WHITE", font=font1)
        draw.text((35, 120), "B:强制退出", fill="RED", font=font1)
    else:
        draw.text((35, 80), "A:Host Mode  D:Client Mode", fill="WHITE", font=font1)
        draw.text((35, 120), "B:Force Exit", fill="RED", font=font1)
    display.ShowImage(splash)
    
    # 强制退出检测
    if button.press_b():
        dog.reset()
        sys.exit(0)
    
    # 模式选择
    if button.press_a():
        host_mode()
    elif button.press_d():
        client_mode()
    
    time.sleep(0.1)