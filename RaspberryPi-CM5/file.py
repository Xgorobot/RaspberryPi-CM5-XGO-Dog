import subprocess
import time
from datetime import datetime

# 配置参数
LOG_FILE = "/home/pi/RaspberryPi-CM4/raspberrypi_temp.log"  # 日志文件路径
INTERVAL = 1  # 采样间隔(秒)
MAX_RECORDS = 86400  # 最大记录数，防止文件过大

def get_temp():
    """获取CPU温度"""
    try:
        result = subprocess.check_output(['vcgencmd', 'measure_temp']).decode('utf-8')
        return result.strip().replace("temp=", "")
    except Exception as e:
        return f"ERROR: {str(e)}"

def get_clock():
    """获取ARM时钟频率"""
    try:
        result = subprocess.check_output(['vcgencmd', 'measure_clock', 'arm']).decode('utf-8')
        # 将Hz转换为GHz
        freq = int(result.strip().split("=")[1]) / 1e9
        return f"{freq:.3f}GHz"
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    print(f"开始记录温度和频率到 {LOG_FILE}，按 Ctrl+C 停止")
    
    try:
        with open(LOG_FILE, 'w') as f:
            f.write("时间\t\t\t温度\t\t频率\n")  # 写入表头
            
        record_count = 0
        while record_count < MAX_RECORDS:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temp = get_temp()
            clock = get_clock()
            
            log_entry = f"{timestamp}\t{temp}\t{clock}\n"
            print(log_entry.strip())  # 同时打印到控制台
            
            with open(LOG_FILE, 'a') as f:
                f.write(log_entry)
                
            record_count += 1
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()    