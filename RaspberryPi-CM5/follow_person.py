import cv2
import numpy as np
import onnxruntime
import time
from picamera2 import Picamera2

# 定义相机分辨率和用于距离计算的已知参数的常量
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
KNOWN_DISTANCE = 76.2  # 从相机到人脸的示例已知距离
KNOWN_WIDTH = 14.3  # 人脸的示例已知宽度
FOCAL_LENGTH = 500  # 相机的预设焦距

# 打开摄像头
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 240)}))
picam2.start()
print("摄像头初始化完毕")


class HumanDetector:
    def __init__(self):
        self.session = onnxruntime.InferenceSession('/home/pi/RaspberryPi-CM5/model/Model.onnx')
        self.prev_time = time.time()
        self.frame_count = 0

    def sigmoid(self, x):
        return 1. / (1 + np.exp(-x))

    def tanh(self, x):
        return 2. / (1 + np.exp(-2 * x)) - 1

    def preprocess(self, src_img, size):
        output = cv2.resize(src_img, (size[0], size[1]), interpolation=cv2.INTER_AREA)
        output = output.transpose(2, 0, 1)
        output = output.reshape((1, 3, size[1], size[0])) / 255
        return output.astype('float32')

    def nms(self, dets, thresh=0.45):
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        scores = dets[:, 4]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(ovr <= thresh)[0]
            order = order[inds + 1]
        output = []
        for i in keep:
            output.append(dets[i].tolist())
        return output

    def detection(self, session, img, input_width, input_height, thresh):
        try:
            pred = []
            H, W, _ = img.shape
            data = self.preprocess(img, [input_width, input_height])
            input_name = session.get_inputs()[0].name
            feature_map = session.run([], {input_name: data})[0][0]
            feature_map = feature_map.transpose(1, 2, 0)
            feature_map_height = feature_map.shape[0]
            feature_map_width = feature_map.shape[1]
            for h in range(feature_map_height):
                for w in range(feature_map_width):
                    data = feature_map[h][w]
                    obj_score, cls_score = data[0], data[5:].max()
                    score = (obj_score ** 0.6) * (cls_score ** 0.4)
                    if score > thresh:
                        cls_index = np.argmax(data[5:])
                        x_offset, y_offset = self.tanh(data[1]), self.tanh(data[2])
                        box_width, box_height = self.sigmoid(data[3]), self.sigmoid(data[4])
                        box_cx = (w + x_offset) / feature_map_width
                        box_cy = (h + y_offset) / feature_map_height
                        x1, y1 = box_cx - 0.5 * box_width, box_cy - 0.5 * box_height
                        x2, y2 = box_cx + 0.5 * box_width, box_cy + 0.5 * box_height
                        x1, y1, x2, y2 = int(x1 * W), int(y1 * H), int(x2 * W), int(y2 * H)
                        pred.append([x1, y1, x2, y2, score, cls_index])
            return self.nms(np.array(pred))
        except:
            return None

    def object_data(self, image):
        input_width, input_height = 352, 352
        bboxes = self.detection(self.session, image, input_width, input_height, 0.65)
        return bboxes

    def distance_finder(self, focal_length, real_width, width_in_rf_image):
        distance = (real_width * focal_length) / width_in_rf_image
        return distance

    def detect_humans(self, image):
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.prev_time
        if elapsed_time >= 1:
            fps = self.frame_count / elapsed_time
            print(f"推理帧率: {fps:.2f} FPS")
            self.prev_time = current_time
            self.frame_count = 0

        bboxes = self.object_data(image)
        closest_human = None
        min_distance = float('inf')

        if bboxes:
            for bbox in bboxes:
                if int(bbox[5]) == 0:  # 检查检测到的类别是否是人
                    x1, y1, x2, y2 = bbox[:4]
                    xx1, yy1, xx2, yy2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                    object_width_in_frame = x2 - x1
                    object_center_x = (x1 + x2) / 2
                    distance = self.distance_finder(FOCAL_LENGTH, KNOWN_WIDTH, object_width_in_frame)

                    if distance < min_distance:
                        min_distance = distance
                        closest_human = {
                            'bbox': (xx1, yy1, xx2, yy2),
                            'center_x': object_center_x,
                            'distance': distance
                        }

        if closest_human:
            xx1, yy1, xx2, yy2 = closest_human['bbox']
            cv2.rectangle(image, (xx1, yy1), (xx2, yy2), (255, 255, 0), 2)

        return [closest_human] if closest_human else []

from track import HumanTracker
from xgolib import XGO
from key import Button
button = Button()
dog = XGO(port="/dev/ttyAMA0", version="xgolite")
dog.attitude('p', -10)
# 使用示例
if __name__ == "__main__":
    tracker = HumanTracker()
    from PIL import Image, ImageDraw
    import xgoscreen.LCD_2inch as LCD_2inch
    splash_theme_color = (255,255,255)
    display = LCD_2inch.LCD_2inch()
    display.Init()
    display.clear()
    # Init Splash
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    display.ShowImage(splash)
    detector = HumanDetector()
    last_move_x_speed = 0.0
    last_turn_speed = 0.0
    filter_coefficient = 0.3  # 滤波系数
    while True:
        frame = picam2.capture_array()
        humans = detector.detect_humans(frame)
        for human in humans:
            if human:
                print("\n=== 更新  ===")
                center_x, distance = human['center_x'], human['distance'] if human else (None, None)
                #print(f"距离最近的人在 ({human['bbox']}), center_x: {human['center_x']}, distance: {human['distance']} cm")
                tracking_params = tracker.update(human)
                if tracking_params['is_detected'] and tracking_params['is_moving']:
                    prediction = tracker.predict_future_position(tracking_params, 0.06)
                    if prediction:
                        pass
                raw_move_x_speed = tracking_params['velocity_x'] * 0.05 + (distance - 100) * 0.1
                if -20 <distance - 70 <  20:
                    raw_move_x_speed = (distance - 70) * 0.3
                else: 
                    raw_move_x_speed = (distance - 70) * 0.2
                raw_turn_speed = tracking_params['velocity_x'] * 0.02
                if 145<center_x<175:
                    raw_turn_speed = 0
                elif 130<center_x<145 or 175< center_x <190:
                    raw_turn_speed = (160 - center_x) * 0.2
                else:
                    raw_turn_speed = (160 - center_x) * 0.15
                move_x_speed = filter_coefficient * last_move_x_speed + (1 - filter_coefficient) * raw_move_x_speed
                turn_speed = filter_coefficient * last_turn_speed + (1 - filter_coefficient) * raw_turn_speed
                max_move_speed = 10.0
                max_turn_speed = 15.0
                move_x_speed = max(-max_move_speed, min(max_move_speed, move_x_speed))
                turn_speed = max(-max_turn_speed, min(max_turn_speed, turn_speed))
                # 更新上一时刻的速度
                last_move_x_speed = move_x_speed
                last_turn_speed = turn_speed
                print(f'距离:{distance}, 中心点偏移：{160-center_x}')
                print(f"移动速度: {move_x_speed:.2f}, 转向速度: {turn_speed:.2f}")
            
                dog.move_x(move_x_speed)
                dog.turn(turn_speed)
                #dog.move_x(0.02 * tracking_params['velocity_y'])
                #dog.turn(tracking_params['velocity_x'])
        if humans == []:
            move_x_speed = 0.03*filter_coefficient * last_move_x_speed 
            turn_speed = 0.03*filter_coefficient * last_turn_speed 
            max_move_speed = 3.0
            max_turn_speed = 3.0
            move_x_speed = max(-max_move_speed, min(max_move_speed, move_x_speed))
            turn_speed = max(-max_turn_speed, min(max_turn_speed, turn_speed))
            dog.move_x(move_x_speed)
            dog.turn(turn_speed)
            print(f"移动速度: {move_x_speed:.2f}, 转向速度: {turn_speed:.2f}")
            last_move_x_speed = move_x_speed
            last_turn_speed = turn_speed
        b, g, r = cv2.split(frame)
        img = cv2.merge((r, g, b))
        imgok = Image.fromarray(img)
        display.ShowImage(imgok)


        
        #cv2.imshow('Human Detection', frame)
        #cv2.imwrite('persondetection.png', frame)
        if button.press_b():
            dog.reset()
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break 