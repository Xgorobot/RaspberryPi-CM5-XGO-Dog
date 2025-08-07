import time
import math
import logging

class HumanTracker:
    """人体追踪器，根据人体位置信息计算追踪运动参数"""
    
    def __init__(self, camera_width=320, camera_height=240, 
                 center_threshold=0.1, distance_threshold=100):
        """
        初始化人体追踪器
        
        参数:
            camera_width: 相机画面宽度
            camera_height: 相机画面高度
            center_threshold: 画面中心区域阈值比例
            distance_threshold: 距离变化阈值(厘米)
        """
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.center_threshold = center_threshold
        self.distance_threshold = distance_threshold
        self.last_center_x = None
        self.last_distance = None
        self.last_update_time = time.time()
        
        # 配置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('HumanTracker')
        
    def update(self, human):
        """
        更新人体位置信息并计算追踪参数
        
        参数:
            human: 包含人体信息的字典，应包含'center_x'和'distance'键
            
        返回:
            包含追踪参数的字典
        """
        # 修正：先判断human是否为None
        if human is None:
            center_x, distance = None, None
        else:
            center_x, distance = human['center_x'], human['distance']
        
        # 记录当前时间
        current_time = time.time()
        time_elapsed = current_time - self.last_update_time
        
        # 初始化追踪参数
        tracking_params = {
            'center_x': center_x,
            'distance': distance,
            'is_detected': human is not None,
            'horizontal_direction': 0,  # -1:左, 0:中, 1:右
            'distance_change': 0,
            'velocity': 0,
            'velocity_x': 0,  # 水平速度(左右)
            'velocity_y': 0,  # 垂直速度(前后)
            'is_moving': False,
            'movement_direction': 0  # 运动方向角度(弧度)
        }
        
        if human:
            # 计算水平方向偏移
            normalized_center = center_x / self.camera_width - 0.5
            if normalized_center < -self.center_threshold:
                tracking_params['horizontal_direction'] = -1  # 向左
            elif normalized_center > self.center_threshold:
                tracking_params['horizontal_direction'] = 1   # 向右
                
            # 如果有历史数据，计算变化量
            if self.last_center_x is not None and self.last_distance is not None:
                # 计算距离变化(前后方向)
                tracking_params['distance_change'] = distance - self.last_distance
                
                # 计算水平位置变化(左右方向)
                # 将像素变化转换为实际距离变化，这里使用简化模型
                # 假设在距离为1米时，100像素对应10厘米的实际距离
                pixel_to_cm = 50.0 / 100  
                center_change = (center_x - self.last_center_x) * pixel_to_cm * (distance / 100)
                print(f'center_change: {center_change:.2f} cm')
                
                # 计算速度 (厘米/秒)
                if time_elapsed > 0:
                    # 水平速度(左右)
                    tracking_params['velocity_x'] = center_change / time_elapsed
                    # 垂直速度(前后)
                    tracking_params['velocity_y'] = tracking_params['distance_change'] / time_elapsed
                    # 合速度
                    tracking_params['velocity'] = math.sqrt(
                        tracking_params['velocity_x']**2 + tracking_params['velocity_y']**2
                    )
                    # 运动方向角度(弧度)
                    tracking_params['movement_direction'] = math.atan2(
                        tracking_params['velocity_x'], tracking_params['velocity_y']
                    )
                    # 判断是否在移动
                    tracking_params['is_moving'] = abs(tracking_params['velocity']) > 5  # 速度阈值5cm/s
            
            # 记录当前信息为历史数据
            self.last_center_x = center_x
            self.last_distance = distance
            self.last_update_time = current_time
            
            self.logger.info(f"检测到人体: 中心位置={center_x}, 距离={distance}cm, "
                            f"水平速度={tracking_params['velocity_x']:.1f}cm/s, "
                            f"垂直速度={tracking_params['velocity_y']:.1f}cm/s, "
                            f"总速度={tracking_params['velocity']:.1f}cm/s, "
                            f"方向角={math.degrees(tracking_params['movement_direction']):.1f}°")
        else:
            self.logger.warning("未检测到人体")
            # 重置历史数据
            self.last_center_x = None
            self.last_distance = None
            
        return tracking_params
    
    def predict_future_position(self, current_params, prediction_time=0.5):
        """
        预测未来时间点的人体位置
        
        参数:
            current_params: 当前追踪参数
            prediction_time: 预测时间(秒)
            
        返回:
            预测的位置信息
        """
        if not current_params['is_detected'] or not current_params['is_moving']:
            return None
            
        # 预测未来距离(前后方向)
        predicted_distance = current_params['distance'] + current_params['velocity_y'] * prediction_time
        
        # 预测水平方向移动(左右方向)
        # 将速度(cm/s)转换为像素/秒
        cm_to_pixel = 100 / 10.0  # 在1米距离下，10厘米对应100像素
        horizontal_movement = current_params['velocity_x'] * prediction_time * cm_to_pixel * (predicted_distance / 100)
        
        predicted_center_x = self.last_center_x + horizontal_movement
        
        # 确保预测的中心位置在画面范围内
        predicted_center_x = max(0, min(self.camera_width, predicted_center_x))
        
        return {
            'center_x': predicted_center_x,
            'distance': predicted_distance,
            'prediction_time': prediction_time
        }

# 使用示例
if __name__ == "__main__":
    # 创建追踪器实例
    tracker = HumanTracker()
    
    # 模拟人体数据
    human_data = [
        {'center_x': 320, 'distance': 200},
        {'center_x': 340, 'distance': 190},  # 向右前方移动
        {'center_x': 360, 'distance': 185},  # 继续向右前方移动
        {'center_x': 350, 'distance': 175},  # 向左前方移动
        {'center_x': 330, 'distance': 170},  # 继续向左前方移动
        None,  # 丢失目标
        {'center_x': 320, 'distance': 200}   # 重新检测到
    ]
    
    # 模拟追踪过程
    for i, data in enumerate(human_data):
        print(f"\n=== 更新 {i+1} ===")
        tracking_params = tracker.update(data)
        
        # 预测未来位置
        if tracking_params['is_detected'] and tracking_params['is_moving']:
            prediction = tracker.predict_future_position(tracking_params, 0.06)
            if prediction:
                print(f"预测0.06秒后位置: 中心={prediction['center_x']:.1f}, 距离={prediction['distance']:.1f}cm")
        
        # 模拟时间流逝