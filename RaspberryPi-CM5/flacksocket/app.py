import os
import sys
import time
import threading
import cv2 as cv
import xgoscreen.LCD_2inch as LCD_2inch
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, Response, redirect
from flask_socketio import SocketIO, send, emit
from camera_dog import Dog_Camera
from concurrent.futures import ThreadPoolExecutor

os.environ['PATH'] = '/home/pi/RaspberryPi-CM4/xgovenv/bin:' + os.environ.get('PATH', '')
os.chdir('/home/pi/RaspberryPi-CM4')  

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from demos.uiutils import (Button, splash_theme_color, btn_selected, btn_unselected, txt_selected, 
                          txt_unselected, dog, color_white, color_red, display, splash, get_font, 
                          draw, color_black, lcd_draw_string, lcd_rect, lal)

# Init Splash
display.ShowImage(splash)

# Load Images
app_image = Image.open("/home/pi/RaspberryPi-CM4/pics/app.png") 
unapp_image = Image.open("/home/pi/RaspberryPi-CM4/pics/unapp.png")
wifiy = Image.open("/home/pi/RaspberryPi-CM4/pics/wifi@2x.jpg")
wifin = Image.open("/home/pi/RaspberryPi-CM4/pics/wifi-un@2x.jpg")
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 23)

def get_ip(ifname):
    import socket, struct, fcntl
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(), 
        0x8915, 
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])

def ip():
    try:
        ipchr = get_ip('wlan0')
    except:
        ipchr = '0.0.0.0'
    return ipchr

# Thread management
exit_event = threading.Event()
button = Button()
executor = ThreadPoolExecutor(max_workers=4)

class CameraHandler:
    def __init__(self):
        self.camera = Dog_Camera(debug=False)
        self.lock = threading.Lock()
        
    def get_frame(self):
        with self.lock:
            success, frame = self.camera.get_frame()
            if not success:
                self.camera.reconnect()
                return None
            return frame

camera_handler = CameraHandler()

def check_button():
    while not exit_event.is_set():
        if button.press_b():
            print("Button B Pressed! Exiting gracefully...")
            dog.reset()
            exit_event.set()
            os._exit(0)
        time.sleep(0.1)

button_thread = threading.Thread(target=check_button)
button_thread.daemon = True
button_thread.start()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Record Last Access Time
last_access_time = 0

def monitor_connection():
    global last_access_time
    ipadd = ip()

    ip_with_port = f"{ipadd}:8080"  
    print(ip_with_port)  
    
    while not exit_event.is_set():

        lcd_rect(0, 180, 320, 240, color=color_black, thickness=-1)
        lcd_draw_string(draw, 70, 200, ip_with_port, color=color_white, scale=font2)
        
        current_time = time.time()
        if current_time - last_access_time > 10:
            splash.paste(unapp_image, (0, 0))
            splash.paste(wifiy, (20, 200)) 
            display.ShowImage(splash)
        else:
            splash.paste(app_image, (0, 0))
            splash.paste(wifiy, (40, 200))  
            display.ShowImage(splash)
        time.sleep(2)

def video_handle():
    while not exit_event.is_set():
        frame = camera_handler.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
            
        try:
            ret, img_encode = cv.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + img_encode.tobytes() + b'\r\n')
        except Exception as e:
            print(f"Video encoding error: {e}")
            time.sleep(0.1)

def execute_action(action_func, *args):
    try:
        action_func(*args)
    except Exception as e:
        print(f"Action error: {e}")

@app.route('/')
def index():
    global last_access_time
    last_access_time = time.time()
    ip_address = get_ip('wlan0')
    return render_template('demo.html', device_ip=ip_address)
    
@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_handle(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def on_connect():  
    print('Client connected')
    
@socketio.on('disconnect')
def on_disconnect():  
    print('Client disconnected')

# Action handlers
@socketio.on('balance')  
def handle_balance(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.imu, int(data))

@socketio.on('reset')  
def handle_reset(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.reset)
    emit('reset_height', {'value': 50}, broadcast=True)
@socketio.on('action')  
def handle_action(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.perform, int(data))
    
@socketio.on('PushUp')  
def handle_pushup(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.action, int(data))
    
@socketio.on('TakeAPee')  
def handle_takeapee(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.action, int(data))
    
@socketio.on('WaveHand')  
def handle_wavehand(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.action, int(data))

@socketio.on('UpDown')  
def handle_updown(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.action, int(data))

@socketio.on('LookFood')  
def handle_lookfoot(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.action, int(data))

@socketio.on('Dance')  
def handle_dance(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.action, int(data))

@socketio.on('up')  
def handle_up(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.move_x, int(data))

@socketio.on('down')  
def handle_down(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.move_x, int(data))

@socketio.on('left')  
def handle_left(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.move_y, int(data))

@socketio.on('right')  
def handle_right(data):  
    global last_access_time
    last_access_time = time.time()
    executor.submit(execute_action, dog.move_y, int(data))

@socketio.on('height')
def handle_height(data):
    global last_access_time
    last_access_time = time.time()
    data = int(data)
    
    # Map 0-100 slider to range with 50 at 95
    if data < 50:
        height = int(95 - (50 - data) * 1.0)  # Adjust multiplier as needed
    else:
        height = int(95 + (data - 50) * 1.0)  # Adjust multiplier as needed
    
    # Ensure within safe bounds
    height = max(30, min(160, height))
    
    executor.submit(execute_action, lambda: dog.translation('z', height))

def run_flask():
    socketio.run(
    app, 
    host='0.0.0.0', 
    port=8080, 
    debug=False, 
    use_reloader=False,
    allow_unsafe_werkzeug=True 
)


if __name__ == '__main__':
    # Start monitor thread
    monitor_thread = threading.Thread(target=monitor_connection)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Start Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    try:
        while not exit_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        exit_event.set()
        dog.reset()
    
    print("App exited cleanly")
