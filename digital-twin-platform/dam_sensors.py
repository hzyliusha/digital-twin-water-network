import json
import time
import random
import threading
import requests
from datetime import datetime
import math

class DamSensorSimulator:
    def __init__(self, dam_id="DAM001"):
        self.dam_id = dam_id
        self.running = False
        self.base_water_level = 85.0  # 基础水位 (米)
        self.base_pressure = 120.0    # 基础压力 (kPa)
        self.base_flow_rate = 150.0   # 基础流量 (m³/s)
        
    def generate_sensor_data(self):
        """生成模拟传感器数据"""
        current_time = datetime.now()
        
        # 模拟水位变化（受时间和随机因素影响）
        time_factor = math.sin(time.time() / 3600) * 2  # 小时级波动
        water_level = self.base_water_level + time_factor + random.uniform(-0.5, 0.5)
        
        # 模拟坝体压力（与水位相关）
        pressure = self.base_pressure + (water_level - self.base_water_level) * 1.5 + random.uniform(-2, 2)
        
        # 模拟流量（与水位和时间相关）
        flow_rate = self.base_flow_rate + (water_level - self.base_water_level) * 2 + random.uniform(-5, 5)
        
        # 模拟温度
        temperature = 15 + math.sin(time.time() / 86400 * 2 * math.pi) * 8 + random.uniform(-1, 1)
        
        # 模拟位移传感器（毫米）
        displacement_x = random.uniform(-0.2, 0.2)
        displacement_y = random.uniform(-0.1, 0.1)
        displacement_z = random.uniform(-0.3, 0.1)
        
        # 模拟渗流量
        seepage = max(0, random.uniform(0.5, 2.5))
        
        # 确保所有数值都是有效的浮点数
        water_level = round(max(0, water_level), 2)
        pressure = round(max(0, pressure), 2)
        flow_rate = round(max(0, flow_rate), 2)
        temperature = round(temperature, 2)
        
        return {
            "dam_id": self.dam_id,
            "timestamp": current_time.isoformat(),
            "sensors": {
                "water_level": water_level,
                "pressure": pressure,
                "flow_rate": flow_rate,
                "temperature": temperature,
                "displacement": {
                    "x": round(displacement_x, 3),
                    "y": round(displacement_y, 3),
                    "z": round(displacement_z, 3)
                },
                "seepage": round(seepage, 3)
            },
            "status": self.check_status(water_level, pressure, flow_rate)
        }
    
    def check_status(self, water_level, pressure, flow_rate):
        """检查大坝状态"""
        if water_level > 90 or pressure > 140 or flow_rate > 200:
            return "WARNING"
        elif water_level > 95 or pressure > 160 or flow_rate > 250:
            return "CRITICAL"
        return "NORMAL"
    
    def send_to_edge_server(self, data, edge_server_url="http://localhost:8001/receive_data"):
        """通过无线网络发送数据到边缘服务器"""
        try:
            response = requests.post(edge_server_url, json=data, timeout=5)
            if response.status_code == 200:
                print(f"数据已发送到边缘服务器: {data['timestamp']}")
            else:
                print(f"发送失败: {response.status_code}")
        except Exception as e:
            print(f"网络错误: {e}")
    
    def start_simulation(self, interval=10):
        """启动传感器数据模拟"""
        self.running = True
        print(f"大坝 {self.dam_id} 传感器开始工作...")
        
        while self.running:
            data = self.generate_sensor_data()
            print(f"生成数据: 水位={data['sensors']['water_level']}m, "
                  f"压力={data['sensors']['pressure']}kPa, "
                  f"状态={data['status']}")
            
            # 发送到边缘服务器
            self.send_to_edge_server(data)
            
            time.sleep(interval)
    
    def stop_simulation(self):
        """停止模拟"""
        self.running = False
        print("传感器模拟已停止")

if __name__ == "__main__":
    simulator = DamSensorSimulator()
    try:
        simulator.start_simulation(interval=5)  # 每5秒发送一次数据
    except KeyboardInterrupt:
        simulator.stop_simulation() 