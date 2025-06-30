"""
水网边缘节点程序，负责数据采集、预处理和本地决策
"""
import os
import sys
import json
import time
import datetime
import threading
import queue
import logging
import paho.mqtt.client as mqtt
import numpy as np
import pandas as pd
import requests
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import EDGE_CONFIG, MQTT_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"edge_{EDGE_CONFIG['id']}.log")
    ]
)
logger = logging.getLogger("edge_node")

# 数据缓冲队列
data_buffer = queue.Queue(maxsize=EDGE_CONFIG['buffer_size'])

# 本地存储目录
local_storage_path = Path(EDGE_CONFIG['local_storage_path'])
local_storage_path.mkdir(parents=True, exist_ok=True)

# 设备列表
devices = {}

# MQTT客户端设置
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT连接结果: {rc}")
    client.subscribe(MQTT_CONFIG['topic_telemetry'])
    client.subscribe(MQTT_CONFIG['topic_command'])

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.debug(f"收到消息: {msg.topic} {payload}")
        
        if msg.topic == MQTT_CONFIG['topic_telemetry']:
            # 处理遥测数据
            process_telemetry(payload)
        
        elif msg.topic == MQTT_CONFIG['topic_command']:
            # 处理命令
            process_command(payload)
    
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def process_telemetry(data):
    """处理遥测数据"""
    try:
        # 添加时间戳和边缘节点ID
        data['edge_timestamp'] = datetime.datetime.now().isoformat()
        data['edge_id'] = EDGE_CONFIG['id']
        
        # 数据预处理
        if 'flow_rate' in data and isinstance(data['flow_rate'], (int, float)):
            # 流量异常检测
            if data['flow_rate'] < 0 or data['flow_rate'] > 2000:
                logger.warning(f"检测到流量异常值: {data['flow_rate']}")
                data['flow_rate_anomaly'] = True
            else:
                data['flow_rate_anomaly'] = False
                
        if 'pressure' in data and isinstance(data['pressure'], (int, float)):
            # 压力异常检测
            if data['pressure'] < 0 or data['pressure'] > 12:
                logger.warning(f"检测到压力异常值: {data['pressure']}")
                data['pressure_anomaly'] = True
            else:
                data['pressure_anomaly'] = False
                
        if 'water_quality' in data and isinstance(data['water_quality'], (int, float)):
            # 水质异常检测
            if data['water_quality'] < 50:
                logger.warning(f"检测到水质异常值: {data['water_quality']}")
                data['water_quality_anomaly'] = True
            else:
                data['water_quality_anomaly'] = False
        
        # 添加到缓冲区
        try:
            data_buffer.put(data, block=False)
        except queue.Full:
            logger.warning("数据缓冲区已满，丢弃最早的数据")
            data_buffer.get()  # 移除最早的数据
            data_buffer.put(data)
        
        # 本地存储
        store_data_locally(data)
        
    except Exception as e:
        logger.error(f"处理遥测数据时出错: {e}")

def process_command(command):
    """处理命令"""
    try:
        device_id = command.get('device_id')
        if not device_id:
            logger.error("命令缺少设备ID")
            return
        
        logger.info(f"处理设备 {device_id} 的命令: {command}")
        
        # 转发命令到设备
        # 在实际应用中，这里可能需要根据设备的连接方式进行不同的处理
        # 例如通过串口、蓝牙、ZigBee等方式发送命令
        
        # 更新设备状态
        if device_id in devices:
            command_type = command.get('command_type')
            
            if command_type == 'status':
                if device_id.startswith('valve'):
                    # 阀门状态控制
                    devices[device_id]['status'] = command.get('value', 'unknown')
                elif device_id.startswith('pump'):
                    # 水泵状态控制
                    devices[device_id]['status'] = command.get('value', 'unknown')
                
                # 发送状态更新到云端
                status_update = {
                    'device_id': device_id,
                    'status': devices[device_id]['status'],
                    'edge_id': EDGE_CONFIG['id'],
                    'timestamp': datetime.datetime.now().isoformat()
                }
                mqtt_client.publish(MQTT_CONFIG['topic_status'], json.dumps(status_update))
                
            elif command_type == 'parameter':
                param_name = command.get('parameter')
                param_value = command.get('value')
                
                if param_name and param_value is not None:
                    if 'parameters' not in devices[device_id]:
                        devices[device_id]['parameters'] = {}
                    
                    devices[device_id]['parameters'][param_name] = param_value
                    
                    # 特殊处理
                    if device_id.startswith('valve') and param_name == 'opening':
                        # 阀门开度调整
                        logger.info(f"调整阀门 {device_id} 开度为 {param_value}%")
                    elif device_id.startswith('pump') and param_name == 'power':
                        # 水泵功率调整
                        logger.info(f"调整水泵 {device_id} 功率为 {param_value}%")
        else:
            logger.warning(f"未找到设备 {device_id}")
        
    except Exception as e:
        logger.error(f"处理命令时出错: {e}")

def store_data_locally(data):
    """本地存储数据"""
    try:
        device_id = data.get('device_id')
        if not device_id:
            return
        
        # 按设备ID和日期组织文件
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        device_dir = local_storage_path / device_id
        device_dir.mkdir(exist_ok=True)
        
        file_path = device_dir / f"{today}.jsonl"
        
        # 追加写入JSON行
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
            
    except Exception as e:
        logger.error(f"本地存储数据时出错: {e}")

def sync_data_to_cloud():
    """同步数据到云端"""
    while True:
        try:
            # 等待指定的同步间隔
            time.sleep(EDGE_CONFIG['cloud_sync_interval'])
            
            if data_buffer.empty():
                continue
            
            logger.info(f"开始同步数据到云端，当前缓冲区大小: {data_buffer.qsize()}")
            
            # 批量获取数据
            batch_size = min(100, data_buffer.qsize())
            batch_data = []
            
            for _ in range(batch_size):
                if not data_buffer.empty():
                    batch_data.append(data_buffer.get())
            
            if not batch_data:
                continue
                
            # 发送数据到云端
            for data in batch_data:
                mqtt_client.publish(MQTT_CONFIG['topic_telemetry'], json.dumps(data))
                
            logger.info(f"已同步 {len(batch_data)} 条数据到云端")
            
        except Exception as e:
            logger.error(f"同步数据到云端时出错: {e}")

def process_data_periodically():
    """定期处理数据"""
    while True:
        try:
            # 等待指定的处理间隔
            time.sleep(EDGE_CONFIG['processing_interval'])
            
            if data_buffer.empty():
                continue
            
            logger.debug(f"开始处理数据，当前缓冲区大小: {data_buffer.qsize()}")
            
            # 获取所有数据进行批处理
            temp_data = []
            while not data_buffer.empty():
                temp_data.append(data_buffer.get())
                
            if not temp_data:
                continue
            
            # 按设备分组
            device_data = {}
            for item in temp_data:
                device_id = item.get('device_id')
                if device_id:
                    if device_id not in device_data:
                        device_data[device_id] = []
                    device_data[device_id].append(item)
            
            # 处理每个设备的数据
            for device_id, items in device_data.items():
                # 根据设备类型进行不同的处理
                if device_id.startswith('water_sensor'):
                    process_water_sensor_data(device_id, items)
                elif device_id.startswith('valve'):
                    process_valve_data(device_id, items)
                elif device_id.startswith('pump'):
                    process_pump_data(device_id, items)
            
            # 将处理后的数据重新放回缓冲区
            for item in temp_data:
                try:
                    data_buffer.put(item, block=False)
                except queue.Full:
                    # 缓冲区已满，不再放回
                    pass
                
        except Exception as e:
            logger.error(f"定期处理数据时出错: {e}")

def process_water_sensor_data(device_id, items):
    """处理水质传感器数据"""
    try:
        # 提取数据
        flow_rates = [item['flow_rate'] for item in items if 'flow_rate' in item]
        pressures = [item['pressure'] for item in items if 'pressure' in item]
        water_qualities = [item['water_quality'] for item in items if 'water_quality' in item]
        temperatures = [item['temperature'] for item in items if 'temperature' in item]
        
        # 计算统计值
        if flow_rates:
            avg_flow = np.mean(flow_rates)
            max_flow = np.max(flow_rates)
            min_flow = np.min(flow_rates)
            std_flow = np.std(flow_rates)
            logger.info(f"设备 {device_id} 流量统计: 平均={avg_flow:.2f}, 最大={max_flow:.2f}, 最小={min_flow:.2f}, 标准差={std_flow:.2f}")
            
            # 流量异常检测 (突变检测)
            if len(flow_rates) > 5 and std_flow > 100:
                logger.warning(f"设备 {device_id} 流量波动异常: 标准差={std_flow:.2f}")
        
        if pressures:
            avg_pressure = np.mean(pressures)
            max_pressure = np.max(pressures)
            min_pressure = np.min(pressures)
            std_pressure = np.std(pressures)
            logger.info(f"设备 {device_id} 压力统计: 平均={avg_pressure:.2f}, 最大={max_pressure:.2f}, 最小={min_pressure:.2f}, 标准差={std_pressure:.2f}")
            
            # 压力异常检测
            if max_pressure > 8 or min_pressure < 1:
                logger.warning(f"设备 {device_id} 压力异常: {min_pressure:.2f} - {max_pressure:.2f}")
        
        if water_qualities:
            avg_quality = np.mean(water_qualities)
            min_quality = np.min(water_qualities)
            logger.info(f"设备 {device_id} 水质统计: 平均={avg_quality:.2f}, 最低={min_quality:.2f}")
            
            # 水质异常检测
            if min_quality < 60:
                logger.warning(f"设备 {device_id} 水质不达标: 最低值={min_quality:.2f}")
                
        if temperatures:
            avg_temp = np.mean(temperatures)
            logger.info(f"设备 {device_id} 水温统计: 平均={avg_temp:.2f}")
    
    except Exception as e:
        logger.error(f"处理水质传感器数据时出错: {e}")

def process_valve_data(device_id, items):
    """处理阀门数据"""
    try:
        # 提取数据
        statuses = [item['status'] for item in items if 'status' in item]
        openings = [item['opening'] for item in items if 'opening' in item]
        actual_openings = [item['actual_opening'] for item in items if 'actual_opening' in item]
        flow_rates = [item['flow_rate'] for item in items if 'flow_rate' in item]
        
        if openings and actual_openings:
            # 检查实际开度与设定开度的偏差
            deviations = [abs(actual - setting) for actual, setting in zip(actual_openings, openings)]
            avg_deviation = np.mean(deviations)
            max_deviation = np.max(deviations)
            
            if max_deviation > 5:
                logger.warning(f"阀门 {device_id} 开度偏差较大: 平均={avg_deviation:.2f}, 最大={max_deviation:.2f}")
                
        if flow_rates:
            avg_flow = np.mean(flow_rates)
            logger.info(f"阀门 {device_id} 平均流量: {avg_flow:.2f}")
            
            # 检查阀门状态与流量是否匹配
            if 'closed' in statuses and avg_flow > 10:
                logger.warning(f"阀门 {device_id} 状态为关闭但检测到流量: {avg_flow:.2f}")
    
    except Exception as e:
        logger.error(f"处理阀门数据时出错: {e}")

def process_pump_data(device_id, items):
    """处理水泵数据"""
    try:
        # 提取数据
        powers = [item['power'] for item in items if 'power' in item]
        actual_powers = [item['actual_power'] for item in items if 'actual_power' in item]
        rpms = [item['rpm'] for item in items if 'rpm' in item]
        actual_rpms = [item['actual_rpm'] for item in items if 'actual_rpm' in item]
        flow_rates = [item['flow_rate'] for item in items if 'flow_rate' in item]
        pressures = [item['pressure'] for item in items if 'pressure' in item]
        energy_consumptions = [item['energy_consumption'] for item in items if 'energy_consumption' in item]
        
        if powers and actual_powers:
            # 检查实际功率与设定功率的偏差
            deviations = [abs(actual - setting) for actual, setting in zip(actual_powers, powers)]
            avg_deviation = np.mean(deviations)
            max_deviation = np.max(deviations)
            
            if max_deviation > 10:
                logger.warning(f"水泵 {device_id} 功率偏差较大: 平均={avg_deviation:.2f}, 最大={max_deviation:.2f}")
        
        if flow_rates and powers:
            # 计算效率 (流量/功率)
            efficiencies = [flow / power if power > 0 else 0 for flow, power in zip(flow_rates, powers)]
            avg_efficiency = np.mean([e for e in efficiencies if e > 0])
            
            logger.info(f"水泵 {device_id} 平均效率: {avg_efficiency:.2f}")
            
            # 检测效率异常
            if avg_efficiency < 10:
                logger.warning(f"水泵 {device_id} 效率较低: {avg_efficiency:.2f}")
        
        if energy_consumptions:
            # 计算总能耗
            total_energy = sum(energy_consumptions)
            logger.info(f"水泵 {device_id} 周期能耗: {total_energy:.4f} kWh")
    
    except Exception as e:
        logger.error(f"处理水泵数据时出错: {e}")

def discover_devices():
    """发现和注册设备"""
    # 这里可以实现自动发现设备的逻辑
    # 例如通过广播、扫描网络等方式
    
    # 模拟一些预定义的设备
    mock_devices = [
        {'device_id': 'water_sensor-001', 'type': 'water_sensor', 'name': '水质传感器1', 'location': '区域A'},
        {'device_id': 'valve-001', 'type': 'valve', 'name': '控制阀1', 'location': '区域A'},
        {'device_id': 'pump-001', 'type': 'pump', 'name': '水泵1', 'location': '泵站A'}
    ]
    
    for device in mock_devices:
        device_id = device['device_id']
        devices[device_id] = device
        devices[device_id]['status'] = 'online'
        logger.info(f"注册设备: {device_id}")
        
        # 发送设备状态到云端
        status_update = {
            'device_id': device_id,
            'status': 'online',
            'edge_id': EDGE_CONFIG['id'],
            'timestamp': datetime.datetime.now().isoformat()
        }
        mqtt_client.publish(MQTT_CONFIG['topic_status'], json.dumps(status_update))

def main():
    """主函数"""
    try:
        logger.info(f"启动水网边缘节点: {EDGE_CONFIG['id']}")
        
        # 连接MQTT代理
        logger.info(f"连接MQTT代理: {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
        mqtt_client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)
        
        # 启动MQTT循环
        mqtt_client.loop_start()
        
        # 发现和注册设备
        discover_devices()
        
        # 启动数据同步线程
        sync_thread = threading.Thread(target=sync_data_to_cloud)
        sync_thread.daemon = True
        sync_thread.start()
        
        # 启动数据处理线程
        process_thread = threading.Thread(target=process_data_periodically)
        process_thread.daemon = True
        process_thread.start()
        
        # 发送边缘节点状态
        edge_status = {
            'device_id': EDGE_CONFIG['id'],
            'type': 'edge',
            'name': EDGE_CONFIG['name'],
            'location': EDGE_CONFIG['location'],
            'status': 'online',
            'timestamp': datetime.datetime.now().isoformat()
        }
        mqtt_client.publish(MQTT_CONFIG['topic_status'], json.dumps(edge_status))
        
        # 主循环
        while True:
            time.sleep(10)
            # 心跳检测
            edge_heartbeat = {
                'device_id': EDGE_CONFIG['id'],
                'type': 'heartbeat',
                'timestamp': datetime.datetime.now().isoformat()
            }
            mqtt_client.publish(MQTT_CONFIG['topic_status'], json.dumps(edge_heartbeat))
            
    except KeyboardInterrupt:
        logger.info("接收到退出信号，正在关闭...")
    except Exception as e:
        logger.error(f"运行时出错: {e}")
    finally:
        # 发送边缘节点离线状态
        edge_status = {
            'device_id': EDGE_CONFIG['id'],
            'status': 'offline',
            'timestamp': datetime.datetime.now().isoformat()
        }
        mqtt_client.publish(MQTT_CONFIG['topic_status'], json.dumps(edge_status))
        
        # 停止MQTT循环
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("边缘节点已关闭")

if __name__ == "__main__":
    main() 