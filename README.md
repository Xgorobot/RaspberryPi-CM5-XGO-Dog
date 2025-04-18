# RaspberryPi-CM5|树莓派5驱动的四足机器人控制框架
[![Build Status](https://img.shields.io/github/actions/workflow/status/yourname/RaspberryPi-CM5/build.yml?logo=github)](https://github.com/yourname/RaspberryPi-CM5/actions)
[![Coverage](https://img.shields.io/codecov/c/github/yourname/RaspberryPi-CM5?logo=codecov)](https://codecov.io/gh/yourname/RaspberryPi-CM5)  
[![RPi5](https://img.shields.io/badge/Raspberry%20Pi-5-red?logo=raspberrypi)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![License](https://img.shields.io/github/license/yourname/RaspberryPi-CM5)](LICENSE)

## 目录

1. [🚀 快速上手](#快速上手)
   - [硬件准备](#硬件准备)
   - [快速启动步骤](#快速启动步骤)
2. [🔍 项目介绍](#项目介绍)
   - [项目概述](#part1)
   - [核心功能模块介绍](#part2)
3. [⚠️ 注意事项](#注意事项)
   - [环境配置](#part3)
   - [硬件影响](#part4)
4. [📜 更新日志](#更新日志)
5. [🤝 参与开发](#参与开发)
6. [📄 许可证](#许可证)
7. [🙏 致谢](#致谢)

## 快速上手

#### 硬件准备
1. 已安装好系统的树莓派CM5开发板并且配置好Python语言环境
2. 兼容的摄像头模块
3. 电源和网络连接

#### 快速启动步骤
```bash
# 树莓派5默认可能未安装venv，需先确认
sudo apt-get install python3-venv -y 

# 1. 克隆代码
git clone https://github.com/yourusername/RaspberryPi-CM4.git
cd RaspberryPi-CM4

# 2. 创建新的虚拟环境（以后再次开发也需要进入虚拟环境中开发）
python3 -m venv xgovenv  # 新建虚拟环境，命名为xgovenv
source xgovenv/bin/activate  # 激活环境

# 3. 安装依赖
pip install -r requirements.txt  

# 4. 运行主程序
python main.py  

# 5. 退出虚拟环境（完成后）
deactivate
```

>如果对树莓派5的虚拟环境配置有疑问，请参考官网:
>[树莓派官方使用文档](https://www.raspberrypi.com/documentation/computers/getting-started.html)


##  项目介绍

### <a id="part1"></a>一、项目概述
#### 1.1 项目简介
XGO 是一款开源的桌面级四足机器人，采用铝合金结构件与总线舵机设计，支持运动控制、AI扩展和二次开发，适合教育、科研及机器人爱好者。

**核心特点**
- 12自由度灵活运动：每条腿配备3个关节舵机（髋/肩/肘），实现精准步态控制。

- 模块化AI扩展：可拆卸的AI视觉模组（通过串口连接），支持图像识别、语音交互等应用。

- 高强度机身：铝合金框架+3D打印外壳，兼顾轻量化与耐用性。

- 即插即用供电：2节18650锂电池（2S）磁吸固定，底部集成Type-C充电接口。

- 开源生态：提供完整的运动控制库、ROS支持及开发文档，助力快速上手。

适用场景：STEM教育、机器人算法验证、AI应用开发、极客DIY。

#### 1.2 系统架构总览  
RaspberryPi-CM4：主功能文件夹
- flacksocket：图传模式，提供网页远程控制界面，支持视频图传和机器控制
  - templates：前端界面文件
  - static：静态资源配置
  - app：功能主控制逻辑代码
  - camera_dog：摄像头驱动库
- hotspot：热点模式，将设备设为AP模式，显示连接信息
- demos：示例模式
  - dog_show:表演模式，机器人随着音乐变化表情和动作
  - network：无线联网，通过扫描网络二维码，进行联网
  - xiaozhi：接入小智的API进行语音对话和相对应动画显示
  - speech：语言识别，lulu为提示词，识别屏幕中语言，并做相应的动作
    - audio：录音功能
    - language_recognize：语言识别模块
    - libnyumaya：提示词训练模型模块
    - auto_platform:系统自适应模块
  - EI:具身智能模式，基于语言分析的机器人控制模式
    - audio：录音功能
    - language_recognize：语言识别模块
    - libnyumaya：提示词训练模型模块
    - auto_platform:系统自适应模块
  - face_mask:识别人脸，机器人自动操作使得自身方向与人脸摇摆方向一致
  - face_decetion:人脸跟踪，识别人脸并跟随人脸调整，机器人始终对着人脸
  - hands:手势识别，识别手势，进行相应动作
  - hp:隔空控制，检测到大拇指和食指（两指垂直）的距离后，机器人对应蹲下
  - pose_dog:骨骼识别，识别骨骼并随着摆动
  - color:颜色跟踪，识别颜色标注颜色的位置，并跟踪小球
  - qrcode:二维码，获取二维码的内容，并输出到屏幕上
  - group:群组表演，APP控制多台设备同步
  - wifi_set：设置信道，网络信道配置
  - language:语言切换，切换中英文
  - volume:音量设置
  - device:设备信息
- demoen:示例模式集合主文件
- main：系统主入口文件
- language：多语言配置文件
- pics：系统图片资源
- volume：音量配置文件
- model：字体配置文件
- xgovenv：虚拟环境配置文件

>如需了解更多功能介绍，详情请看：
>[陆吾智能中文资料库](quehttps://www.yuque.com/luwudynamics/cn)

### <a id="part2"></a>二、核心功能模块介绍
#### 2.1 图传模式 (flacksocket) 

 **基于树莓派（或类似嵌入式设备）的Wi-Fi热点创建与管理工具**，主要功能包括：  


##### **核心功能**  
1. **随机生成Wi-Fi热点信息**  
   - **SSID**：以 `xgo-` 开头 + 6位随机字符（大写字母+数字）  
   - **密码**：8位随机字符（大小写字母+数字）  
   - 通过 `generate_wifi_ssid()` 和 `generate_wifi_password()` 实现。  

2. **配置并启动热点**  
   - 使用 `nmcli`（NetworkManager命令行工具）创建热点：  
     ```python
     hotspot_cmd = "sudo nmcli device wifi hotspot ssid {} password {}".format(ssid, password)
     ```  
   - 包含网络接口初始化（`wlan0`）、断开现有连接、重启服务等预处理步骤。  

3. **按键触发热点关闭与重启**  
   - 监听物理按键（A/B/C/D），按下后：  
     - 关闭热点（`sudo nmcli connection down Hotspot-7`）  
     - 重启设备（`sudo reboot`）  


##### **关键技术实现**  
| 功能                | 实现方式                                                                 |
|---------------------|--------------------------------------------------------------------------|
| **随机字符串生成**   | `random.choices()` + `string` 模块                                       |
| **热点管理**         | `nmcli` 命令行工具 + `os.system()` 调用                                  |
| **IP地址获取**       | Linux的 `ioctl` 系统调用（通过 `socket` 和 `fcntl` 模块）                |
| **LCD显示控制**      | `Pillow` 库绘图 + 自定义 `lcd_text()` 函数                               |




#### 2.2 热点模式 (hotspot)
 **基于树莓派CM4的智能机器狗控制系统**，结合了 **Flask Web服务、实时视频流、SocketIO通信和LCD屏幕交互** 等功能。以下是核心功能的分解：


##### **1. 核心功能概览**
| 功能模块               | 实现内容                                                                 |
|------------------------|--------------------------------------------------------------------------|
| **Web控制界面**         | 通过浏览器远程控制机器狗动作（移动、跳舞、姿态调整等）                   |
| **实时视频流**          | 通过摄像头提供实时监控画面（MJPG流）                                     |
| **多线程管理**          | 并行处理按钮监听、网络监控、视频流和Web服务                              |
| **硬件动作控制**        | 通过 `dog` 对象控制机器狗执行预设动作（如俯卧撑、挥手等）                |


##### **2. 关键技术实现**
###### **(1) Web服务与通信**
- **Flask框架**：提供Web界面（`demo.html` 和 `camera.html`）
- **SocketIO**：实现实时双向通信（动作指令传输）
- **视频流**：通过OpenCV (`cv2`) 捕获并编码摄像头画面，以MJPEG格式推送（`/video_feed` 端点）

##### **(2) 多线程架构**
```python
ThreadPoolExecutor(max_workers=4)  # 处理并发动作请求
threading.Thread(target=monitor_connection)  # 监控连接状态
threading.Thread(target=run_flask)           # 独立运行Web服务
```


##### **3. 关键代码逻辑**
###### **(1) 视频流处理**
```python
def video_handle():
    while True:
        frame = camera_handler.get_frame()  # 从摄像头获取帧
        ret, img_encode = cv.imencode('.jpg', frame)  # 编码为JPEG
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n' + 
               img_encode.tobytes() + b'\r\n')  # 生成MJPEG流
```

###### **(2) 动作指令处理（示例）**
```python
@socketio.on('Dance')
def handle_dance(data):
    executor.submit(execute_action, dog.action, int(data))  # 线程池执行动作
```



#### 2.3 小智对话
 **基于树莓派的智能语音交互机器人系统**，整合了 **MQTT通信、音频编解码（Opus）、AES加密、LCD动画显示和硬件按钮控制** 等功能。以下是详细解析：



##### **1. 核心功能概览**
| **功能模块**          | **实现内容**                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| **云端通信**          | 通过MQTT协议与服务器交互（连接/指令传输）                                   |
| **语音对讲**          | 支持双向音频流（麦克风采集+扬声器播放），使用Opus编解码+AES-128-CTR加密     |
| **动画系统**          | LCD屏幕显示多种状态动画（等待、说话、识别等），预加载提升性能               |
| **OTA升级**           | 从云端获取最新固件信息（`get_ota_version`）                                |



##### **2. 关键技术实现**
###### **(1) 音频处理流水线**
```python
# 发送端（麦克风→加密传输）
mic → pyaudio采集 → Opus编码 → AES加密 → UDP发送

# 接收端（解密→播放）
UDP接收 → AES解密 → Opus解码 → pyaudio播放
```
- **Opus**：低延迟音频编解码（`opuslib`库）
- **AES-128-CTR**：加密音频流（`cryptography`库）
- **UDP传输**：实时性优于TCP

###### **(2) MQTT通信协议**
```python
mqttc = mqtt.Client(client_id="...")
mqttc.on_connect = on_connect  # 订阅主题
mqttc.on_message = on_message  # 处理服务器指令
mqttc.connect(host="...", port=8883)
```
- **消息类型**：
  - `hello`：初始化音频通道
  - `tts`：控制语音合成动画
  - `listen`：启停录音
  - `goodbye`：结束会话



#### 2.4 具身智能
此功能还在测试阶段，待更新~

## 注意事项

### <a id="part3"></a>（一）环境配置

#### **1. 虚拟环境与系统环境的关系**
- **核心问题**  
  虚拟环境是一个独立的Python运行环境，与系统环境完全隔离。如果在系统环境下直接运行虚拟环境配置的项目，会因为缺少依赖库而报错。

- **典型错误示例**  
  ```bash
  # 在系统环境下运行（未激活虚拟环境）
  python main.py
  # 报错：ModuleNotFoundError: No module named 'xxx'
  ```

- **正确操作流程**  
  ```bash
  # 进入项目目录
  cd /path/to/project
  
  # 激活虚拟环境（每次运行前必须执行）
  source venv/bin/activate
  
  # 检查环境是否激活成功
  which python  # 应该显示虚拟环境路径
  
  # 运行项目
  python main.py
  ```

- **常见误区**  
  有些开发者喜欢在PyCharm等IDE中直接运行，但如果没有正确配置解释器路径，仍然会使用系统环境。必须在IDE中手动选择虚拟环境的Python解释器。

#### **2. 虚拟环境中库仍报错的特殊情况**
- **sudo权限问题**  
  使用sudo会切换至root用户的系统环境，导致虚拟环境失效。

  ```bash
  # 错误示范（会跳过虚拟环境）
  sudo python main.py
  
  # 解决方案A：避免使用sudo
  python main.py
  
  # 解决方案B：如果必须sudo，明确指定虚拟环境python路径
  sudo /path/to/venv/bin/python main.py
  ```

- **文件权限问题**  
  虚拟环境目录需要正确的读写权限：

  ```bash
  # 查看权限
  ls -l venv/
  
  # 修复权限（推荐755）
  chmod -R 755 venv/
  ```

#### **3. 自启动服务的正确配置方式**
- **rc.local的局限性**  
  传统rc.local方式会以root权限运行，导致环境变量丢失。
  这可能会使你的代码无法进行正常功能，一般都是权限问题。可以对你的代码进行适配，或者更改自启动方式。


#### **4. 环境诊断技巧**
- **快速诊断命令集**  
  ```bash
  # 检查Python路径
  which python
  
  # 检查已安装包
  pip list
  
  # 检查环境变量
  printenv | grep PATH
  
  # 检查服务日志
  journalctl -u myapp -f
  ```

#### **5. 特殊场景处理**

- **多Python版本管理**  
  ```bash
  # 查看可用版本
  ls /usr/bin/python*
  
  # 创建指定版本的虚拟环境
  python3.9 -m venv venv39
  ```

#### **终极建议**
1. 永远在激活虚拟环境后操作Python项目
2. 避免使用sudo运行Python脚本
3. 重要部署前先做环境检查

这样既能保持开发环境的整洁，又能确保部署的可靠性。遇到问题时，按照上述诊断流程逐步排查，可以快速定位环境配置问题。

### <a id="part4"></a>（二）硬件影响

#### 1. 电量管理
当设备电量低于20%时，系统会自动进入低功耗模式，这可能会对设备的正常运行产生以下影响：

（1）网络连接方面：
- WiFi和蓝牙连接可能变得不稳定
- 网络传输速率可能明显下降
- 部分需要高功耗的外设可能无法正常工作

（2）性能表现：
- CPU会自动降频运行
- 图形处理性能会有所降低
- 系统响应速度可能变慢

（3）错误提示：
您可能会看到如下错误信息：
```
ping: connect: Network is unreachable
wpa_supplicant[XX]: Failed to initialize control interface
```

#### 2. 散热管理
由于树莓派5的性能提升，其发热量也显著增加，需要特别注意：

**温度监控：**
建议通过以下方式实时监测：
```
watch -n 2 vcgencmd measure_temp
```
温度安全范围：
- 正常范围：<70℃
- 警告阈值：70-80℃（系统会自动降频）
- 危险阈值：>80℃（可能导致系统不稳定）


**请务必注意：**
- 树莓派5必须配备散热装置
- 重要数据建议定期备份
- 建议使用UPS不间断电源供电


## 更新日志
#### v1.1.0 (2025-04-15)
- 初始发布版本

## 参与开发

欢迎通过以下方式参与贡献：
1. **代码提交**
   - Fork项目后通过Pull Request提交
   - 遵循PEP8代码规范
   - 提交前运行`pytest tests/`

2. **问题反馈**
   - 在[Issues]()页面报告BUG
   - 附上复现步骤和环境信息

3. **文档改进**
   - 补充使用案例
   - 翻译多语言文档

4. **硬件适配**
   - 测试不同摄像头兼容性
   - 验证其他型号树莓派运行情况

> 首次贡献建议从`good first issue`标签任务开始

## 许可证
本项目采用 **MIT License** 开源协议

## 致谢

