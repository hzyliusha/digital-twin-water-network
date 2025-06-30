"""
水网设备模拟器，用于生成测试数据
"""
import os
import sys
import json
import time
import random
import datetime
import threading
import logging
import argparse
import paho.mqtt.client as mqtt
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import MQTT_CONFIG, DEVICE_TYPES

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("device_simulator.log")
    ]
)
logger = logging.getLogger("device_simulator")

# 设备列表
devices = []

# MQTT客户端设置
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT连接结果: {rc}")
    client.subscribe(MQTT_CONFIG['topic_command'])

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.debug(f"收到消息: {msg.topic} {payload}")
        
        if msg.topic == MQTT_CONFIG['topic_command']:
            # 处理命令
            process_command(payload)
    
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def process_command(command):
    """处理命令"""
    try:
        device_id = command.get('device_id')
        if not device_id:
            logger.error("命令缺少设备ID")
            return
        
        # 查找设备
        device = next((d for d in devices if d['device_id'] == device_id), None)
        if not device:
            logger.warning(f"未找到设备 {device_id}")
            return
        
        logger.info(f"处理设备 {device_id} 的命令: {command}")
        
        # 更新设备状态
        command_type = command.get('command_type')
        if command_type == 'status':
            device['status'] = command.get('value', device['status'])
            logger.info(f"设备 {device_id} 状态已更新为: {device['status']}")
            
            # 发送状态更新
            status_update = {
                'device_id': device_id,
                'status': device['status'],
                'timestamp': datetime.datetime.now().isoformat()
            }
            mqtt_client.publish(MQTT_CONFIG['topic_status'], json.dumps(status_update))
            
        elif command_type == 'mode':
            device['mode'] = command.get('value', device['mode'])
            logger.info(f"设备 {device_id} 模式已更新为: {device['mode']}")
            
        elif command_type == 'parameter':
            param_name = command.get('parameter')
            param_value = command.get('value')
            if param_name and param_value is not None:
                device['parameters'][param_name] = param_value
                logger.info(f"设备 {device_id} 参数 {param_name} 已更新为: {param_value}")
        
    except Exception as e:
        logger.error(f"处理命令时出错: {e}")

def create_water_sensor(device_id, name, location):
    """创建水质传感器设备"""
    device = {
        'device_id': device_id,
        'type': 'water_sensor',
        'name': name,
        'location': location,
        'status': 'online',
        'parameters': {
            'sampling_rate': DEVICE_TYPES['water_sensor']['sampling_rate']
        }
    }
    return device

def create_valve(device_id, name, location):
    """创建阀门设备"""
    device = {
        'device_id': device_id,
        'type': 'valve',
        'name': name,
        'location': location,
        'status': 'open',
        'mode': 'auto',
        'parameters': {
            'opening': 80  # 开度百分比
        }
    }
    return device

def create_pump(device_id, name, location):
    """创建水泵设备"""
    device = {
        'device_id': device_id,
        'type': 'pump',
        'name': name,
        'location': location,
        'status': 'on',
        'mode': 'auto',
        'parameters': {
            'power': 80,  # 功率百分比
            'rpm': 1800   # 转速
        }
    }
    return device

def generate_water_sensor_data(device):
    """生成水质传感器数据"""
    device_id = device['device_id']
    
    # 基准值
    base_flow = 500.0  # L/min
    base_pressure = 5.0  # MPa
    base_quality = 85.0  # 水质指数
    base_temp = 20.0  # °C
    
    # 添加随机波动
    flow_rate = base_flow + random.uniform(-50, 50)
    pressure = base_pressure + random.uniform(-0.5, 0.5)
    water_quality = base_quality + random.uniform(-5, 5)
    temperature = base_temp + random.uniform(-2, 2)
    
    # 有小概率生成异常值
    if random.random() < 0.02:
        # 随机选择一个参数产生异常
        anomaly_param = random.choice(['flow_rate', 'pressure', 'water_quality'])
        if anomaly_param == 'flow_rate':
            flow_rate = flow_rate * 0.2 if random.random() < 0.5 else flow_rate * 1.8
        elif anomaly_param == 'pressure':
            pressure = pressure * 0.3 if random.random() < 0.5 else pressure * 1.7
        elif anomaly_param == 'water_quality':
            water_quality = max(0, water_quality - random.uniform(30, 50))
    
    data = {
        'device_id': device_id,
        'type': 'telemetry',
        'flow_rate': round(flow_rate, 2),
        'pressure': round(pressure, 2),
        'water_quality': round(water_quality, 2),
        'temperature': round(temperature, 2),
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    return data

def generate_valve_data(device):
    """生成阀门数据"""
    device_id = device['device_id']
    status = device['status']
    mode = device.get('mode', 'auto')
    opening = device['parameters'].get('opening', 0)  # 开度百分比
    
    # 只有在开启状态下才生成有效数据
    if status == 'open' or status == 'partially_open':
        # 实际开度可能与设定值有微小差异
        actual_opening = opening + random.uniform(-2, 2)
        actual_opening = max(0, min(100, actual_opening))
        
        # 计算流量 (基于开度的简单模型)
        flow_rate = (actual_opening / 100) * 1000 * random.uniform(0.9, 1.1)
        
        data = {
            'device_id': device_id,
            'type': 'telemetry',
            'status': status,
            'mode': mode,
            'opening': opening,
            'actual_opening': round(actual_opening, 1),
            'flow_rate': round(flow_rate, 2),
            'timestamp': datetime.datetime.now().isoformat()
        }
    else:
        data = {
            'device_id': device_id,
            'type': 'telemetry',
            'status': status,
            'mode': mode,
            'opening': 0,
            'actual_opening': 0,
            'flow_rate': 0,
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    return data

def generate_pump_data(device):
    """生成水泵数据"""
    device_id = device['device_id']
    status = device['status']
    mode = device.get('mode', 'auto')
    power = device['parameters'].get('power', 0)  # 功率百分比
    rpm = device['parameters'].get('rpm', 0)  # 转速
    
    # 只有在开启状态下才生成有效数据
    if status == 'on':
        # 实际功率和转速可能与设定值有微小差异
        actual_power = power + random.uniform(-3, 3)
        actual_power = max(0, min(100, actual_power))
        
        actual_rpm = rpm + random.uniform(-50, 50)
        actual_rpm = max(0, actual_rpm)
        
        # 计算流量和压力 (基于功率和转速的简单模型)
        flow_rate = (actual_power / 100) * 2000 * random.uniform(0.9, 1.1)
        pressure = (actual_power / 100) * 8 * random.uniform(0.9, 1.1)
        
        # 计算能耗 (kWh)
        energy_consumption = (actual_power / 100) * 75 * random.uniform(0.95, 1.05) / 3600
        
        data = {
            'device_id': device_id,
            'type': 'telemetry',
            'status': status,
            'mode': mode,
            'power': power,
            'actual_power': round(actual_power, 1),
            'rpm': rpm,
            'actual_rpm': round(actual_rpm, 1),
            'flow_rate': round(flow_rate, 2),
            'pressure': round(pressure, 2),
            'energy_consumption': round(energy_consumption, 4),
            'timestamp': datetime.datetime.now().isoformat()
        }
    else:
        data = {
            'device_id': device_id,
            'type': 'telemetry',
            'status': status,
            'mode': mode,
            'power': 0,
            'actual_power': 0,
            'rpm': 0,
            'actual_rpm': 0,
            'flow_rate': 0,
            'pressure': 0,
            'energy_consumption': 0,
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    return data

def device_data_generator(device):
    """设备数据生成器"""
    device_id = device['device_id']
    device_type = device['type']
    
    logger.info(f"启动设备 {device_id} 的数据生成")
    
    while True:
        try:
            # 根据设备类型生成不同的数据
            if device_type == 'water_sensor':
                data = generate_water_sensor_data(device)
                # 传感器数据采样率
                sleep_time = device['parameters'].get('sampling_rate', 1)
            elif device_type == 'valve':
                data = generate_valve_data(device)
                sleep_time = 2  # 阀门数据更新间隔
            elif device_type == 'pump':
                data = generate_pump_data(device)
                sleep_time = 2  # 水泵数据更新间隔
            else:
                logger.warning(f"未知的设备类型: {device_type}")
                break
            
            # 发送数据
            mqtt_client.publish(MQTT_CONFIG['topic_telemetry'], json.dumps(data))
            logger.debug(f"设备 {device_id} 发送数据: {data}")
            
            # 等待下一个采样周期
            time.sleep(sleep_time)
            
        except Exception as e:
            logger.error(f"生成设备 {device_id} 数据时出错: {e}")
            time.sleep(5)  # 出错后等待一段时间再重试

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='水网设备模拟器')
    parser.add_argument('--sensors', type=int, default=3, help='水质传感器数量')
    parser.add_argument('--valves', type=int, default=2, help='阀门数量')
    parser.add_argument('--pumps', type=int, default=2, help='水泵数量')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    try:
        logger.info("启动水网设备模拟器")
        
        # 连接MQTT代理
        logger.info(f"连接MQTT代理: {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
        mqtt_client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)
        
        # 启动MQTT循环
        mqtt_client.loop_start()
        
        # 创建设备
        # 水质传感器
        for i in range(args.sensors):
            device_id = f"water_sensor-{i+1:03d}"
            device = create_water_sensor(
                device_id,
                f"水质传感器{i+1}",
                f"区域{chr(65+i%3)}"
            )
            devices.append(device)
            
            # 启动数据生成线程
            thread = threading.Thread(target=device_data_generator, args=(device,))
            thread.daemon = True
            thread.start()
        
        # 阀门
        for i in range(args.valves):
            device_id = f"valve-{i+1:03d}"
            device = create_valve(
                device_id,
                f"控制阀{i+1}",
                f"区域{chr(65+i%3)}"
            )
            devices.append(device)
            
            # 启动数据生成线程
            thread = threading.Thread(target=device_data_generator, args=(device,))
            thread.daemon = True
            thread.start()
        
        # 水泵
        for i in range(args.pumps):
            device_id = f"pump-{i+1:03d}"
            device = create_pump(
                device_id,
                f"水泵{i+1}",
                f"泵站{chr(65+i%3)}"
            )
            devices.append(device)
            
            # 启动数据生成线程
            thread = threading.Thread(target=device_data_generator, args=(device,))
            thread.daemon = True
            thread.start()
        
        logger.info(f"已创建 {len(devices)} 个设备: {args.sensors} 水质传感器, {args.valves} 阀门, {args.pumps} 水泵")
        
        # 主循环
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("接收到退出信号，正在关闭...")
    except Exception as e:
        logger.error(f"运行时出错: {e}")
    finally:
        # 发送设备离线状态
        for device in devices:
            status_update = {
                'device_id': device['device_id'],
                'status': 'offline',
                'timestamp': datetime.datetime.now().isoformat()
            }
            mqtt_client.publish(MQTT_CONFIG['topic_status'], json.dumps(status_update))
        
        # 停止MQTT循环
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("设备模拟器已关闭")

if __name__ == "__main__":
    main() 