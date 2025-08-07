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

#### 快速启动步骤
```bash

# 1. 克隆代码
git clone https://github.com/yourusername/RaspberryPi-CM5.git
cd RaspberryPi-CM5

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

- 开源生态：提供完整的运动控制库、ROS支持及开发文档，助力快速上手。

适用场景：STEM教育、机器人算法验证、AI应用开发、极客DIY。

#### 1.2 系统架构总览  
RaspberryPi-CM5：主功能文件夹
- flacksocket：图传模式，提供网页远程控制界面，支持视频图传和机器控制
- hotspot：热点模式，将设备设为AP模式，显示连接信息
- AI_gym：AI健身助手，机器人可通过摄像头检测动作并计数。
- face_classification-master：人脸情绪识别，机器人会有对应反应。
- fruits：deepseek水果拉霸游戏
- xiaozhi_test：接入小智的API进行语音对话并实习简单的具身智能功能
- demos：示例模式
  - dog_show:表演模式，机器人随着音乐变化表情和动作
  - network：无线联网，通过扫描网络二维码，进行联网
  - speech
    - speech：语言识别，lulu为提示词，识别屏幕中语言，并做相应的动作
    - audio_xxx：录音功能，xxx对应不同的功能
    - language_recognize：语言识别模块
    - doubao_xxx：对应不同的功能的豆包大模型提示词
    - audio_xxx：录音功能，xxx对应不同的功能
    - language_recognize：语言识别模块
    - doubao_xxx：对应不同的功能的豆包大模型提示词
    - coze：智能体实现具身智能
    - ei：大模型实现具身智能
    - gpt_free：自由对话，并显示表情
  - dog_Joystick:手柄控制
  - ball:自主抓小球
  - follow_line:自主巡线
  - shijiao_UDP:多机示教功能
  - face_mask:识别人脸，机器人自动操作使得自身方向与人脸摇摆方向一致
  - face_decetion:人脸跟踪，识别人脸并跟随人脸调整，机器人始终对着人脸
  - hands:手势识别，识别手势，进行相应动作
  - hp:隔空控制，检测到大拇指和食指（两指垂直）的距离后，机器人对应蹲下
  - color:颜色跟踪，识别颜色标注颜色的位置，并跟踪小球
  - qrcode:二维码，获取二维码的内容，并输出到屏幕上
  - group:群组表演，APP控制多台设备同步
  - wifi_set：设置信道，网络信道配置
  - language:语言切换，切换中英文
  - volume:音量设置
  - device:设备信息
- fru：水果拉霸主文件
- follow_person：人体跟随
- fru：水果拉霸主文件
- face：拍照并记录人脸，下次自动识别人脸
- demoen:示例模式集合主文件
- main：系统主入口文件
- language：多语言配置文件
- pics：系统图片资源
- volume：音量配置文件
- model：字体配置文件
- xgovenv：虚拟环境配置文件

>如需了解更多功能介绍，详情请看：
>[陆吾智能中文资料库](quehttps://www.yuque.com/luwudynamics/cn)


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



## 更新日志
#### v1.1.0 (2025-04-15)
- 初始发布版本
#### 测试版本（2025-8-7）
- 如想要优先体验最新功能，请关注TEST分支。


## 参与开发

欢迎通过以下方式参与贡献：
1. **代码提交**
   - Fork项目后通过Pull Request提交
   - 提交前运行`pytest tests/`

2. **问题反馈**
   - 在[Issues]()页面报告BUG
   - 附上复现步骤和环境信息

## 许可证
本项目采用 **MIT License** 开源协议

## 致谢

