from flask import Flask, request, jsonify
import json
import sqlite3
import threading
import time
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

class EdgeServer:
    def __init__(self):
        self.init_database()
        self.cloud_server_url = "http://localhost:8002/receive_edge_data"
        self.data_buffer = []
        self.buffer_lock = threading.Lock()
        
        # 启动数据处理线程
        self.processing_thread = threading.Thread(target=self.process_and_forward_data)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def init_database(self):
        """初始化边缘数据库"""
        conn = sqlite3.connect('edge_data.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dam_id TEXT,
                timestamp TEXT,
                water_level REAL,
                pressure REAL,
                flow_rate REAL,
                temperature REAL,
                displacement_x REAL,
                displacement_y REAL,
                displacement_z REAL,
                seepage REAL,
                status TEXT,
                processed INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    def store_data(self, data):
        """存储传感器数据到本地数据库"""
        conn = sqlite3.connect('edge_data.db', check_same_thread=False)
        cursor = conn.cursor()
        
        sensors = data['sensors']
        cursor.execute('''
            INSERT INTO sensor_data 
            (dam_id, timestamp, water_level, pressure, flow_rate, temperature,
             displacement_x, displacement_y, displacement_z, seepage, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['dam_id'], data['timestamp'], 
            sensors['water_level'], sensors['pressure'], sensors['flow_rate'],
            sensors['temperature'], sensors['displacement']['x'],
            sensors['displacement']['y'], sensors['displacement']['z'],
            sensors['seepage'], data['status']
        ))
        
        conn.commit()
        conn.close()
    
    def edge_processing(self, data):
        """边缘计算处理：数据预处理和异常检测"""
        sensors = data['sensors']
        
        # 数据平滑处理
        processed_data = data.copy()
        
        # 异常检测
        anomalies = []
        if sensors['water_level'] > 95:
            anomalies.append("水位过高")
        if sensors['pressure'] > 160:
            anomalies.append("压力异常")
        if sensors['flow_rate'] > 250:
            anomalies.append("流量异常")
        if abs(sensors['displacement']['z']) > 0.25:
            anomalies.append("垂直位移异常")
        
        processed_data['anomalies'] = anomalies
        
        # 不添加边缘处理时间戳，避免云端处理错误
        # processed_data['processed_at_edge'] = datetime.now().isoformat()
        
        # 计算健康指数 (0-100)
        health_score = 100
        if sensors['water_level'] > 90:
            health_score -= (sensors['water_level'] - 90) * 5
        if sensors['pressure'] > 130:
            health_score -= (sensors['pressure'] - 130) * 2
        
        processed_data['health_score'] = max(0, min(100, health_score))
        
        return processed_data
    
    def process_and_forward_data(self):
        """处理缓存数据并转发到云端"""
        while True:
            try:
                if self.data_buffer:
                    with self.buffer_lock:
                        batch_data = self.data_buffer.copy()
                        self.data_buffer.clear()
                    
                    # 批量处理数据
                    processed_batch = []
                    for data in batch_data:
                        processed = self.edge_processing(data)
                        processed_batch.append(processed)
                    
                    # 发送到云端
                    if processed_batch:
                        self.send_to_cloud(processed_batch)
                else:
                    # 如果没有新数据，检查数据库中是否有未处理的数据
                    conn = sqlite3.connect('edge_data.db', check_same_thread=False)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM sensor_data
                        WHERE processed = 0
                        ORDER BY timestamp ASC
                        LIMIT 10
                    ''')
                    unprocessed_data = cursor.fetchall()
                    
                    if unprocessed_data:
                        print(f"发现 {len(unprocessed_data)} 条未处理的数据")
                        processed_batch = []
                        
                        for row in unprocessed_data:
                            data = {
                                'dam_id': row[1],
                                'timestamp': row[2],
                                'sensors': {
                                    'water_level': float(row[3]),
                                    'pressure': float(row[4]),
                                    'flow_rate': float(row[5]),
                                    'temperature': float(row[6]),
                                    'displacement': {
                                        'x': float(row[7]),
                                        'y': float(row[8]),
                                        'z': float(row[9])
                                    },
                                    'seepage': float(row[10])
                                },
                                'status': row[11]
                            }
                            
                            processed = self.edge_processing(data)
                            processed_batch.append(processed)
                            
                            # 标记为已处理
                            cursor.execute('''
                                UPDATE sensor_data
                                SET processed = 1
                                WHERE id = ?
                            ''', (row[0],))
                        
                        conn.commit()
                        
                        # 发送到云端
                        if processed_batch:
                            self.send_to_cloud(processed_batch)
                    
                    conn.close()
            except Exception as e:
                print(f"数据处理错误: {e}")
            
            # 每10秒处理一次
            time.sleep(10)
    
    def send_to_cloud(self, batch_data):
        """发送处理后的数据到云数据中心"""
        try:
            print(f"正在发送批量数据到云端: {len(batch_data)} 条记录")
            
            # 确保所有数据字段都是有效的
            for item in batch_data:
                # 确保sensors字段存在
                if 'sensors' not in item:
                    print(f"警告: 数据项缺少sensors字段: {item}")
                    continue
                
                # 确保所有必要的传感器数据存在
                sensors = item['sensors']
                if 'water_level' not in sensors:
                    sensors['water_level'] = 0
                if 'pressure' not in sensors:
                    sensors['pressure'] = 0
                if 'flow_rate' not in sensors:
                    sensors['flow_rate'] = 0
                if 'temperature' not in sensors:
                    sensors['temperature'] = 0
                if 'displacement' not in sensors:
                    sensors['displacement'] = {'x': 0, 'y': 0, 'z': 0}
                if 'seepage' not in sensors:
                    sensors['seepage'] = 0
                
                # 确保状态字段存在
                if 'status' not in item:
                    item['status'] = 'NORMAL'
            
            response = requests.post(self.cloud_server_url, json={
                "batch_data": batch_data,
                "edge_server_id": "EDGE001",
                "batch_timestamp": datetime.now().isoformat()
            }, timeout=10)
            
            if response.status_code == 200:
                print(f"批量数据已发送到云端: {len(batch_data)} 条记录")
                print(f"云端响应: {response.text[:100]}...")
            else:
                print(f"云端发送失败: {response.status_code}")
                print(f"错误信息: {response.text[:200]}")
        except Exception as e:
            print(f"云端连接错误: {e}")

edge_server = EdgeServer()

@app.route('/receive_data', methods=['POST'])
def receive_sensor_data():
    """接收传感器数据"""
    try:
        data = request.json
        print(f"接收到传感器数据: {data['dam_id']} - {data['status']}")
        
        # 存储到本地数据库
        edge_server.store_data(data)
        
        # 添加到处理缓冲区
        with edge_server.buffer_lock:
            edge_server.data_buffer.append(data)
        
        return jsonify({"status": "success", "message": "数据已接收"}), 200
    
    except Exception as e:
        print(f"数据接收错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_edge_status():
    """获取边缘服务器状态"""
    conn = sqlite3.connect('edge_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM sensor_data')
    total_records = cursor.fetchone()[0]
    conn.close()
    
    return jsonify({
        "edge_server_id": "EDGE001",
        "status": "online",
        "total_records": total_records,
        "buffer_size": len(edge_server.data_buffer),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("边缘服务器启动中...")
    app.run(host='0.0.0.0', port=8001, debug=False) 