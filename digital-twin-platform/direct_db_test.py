import sqlite3
import json
from datetime import datetime

def get_latest_data():
    """直接从数据库获取最新数据"""
    conn = sqlite3.connect('cloud_data.db')
    cursor = conn.cursor()
    
    # 获取最新数据
    cursor.execute('''
        SELECT * FROM dam_sensor_data 
        ORDER BY id DESC LIMIT 1
    ''')
    latest_data = cursor.fetchone()
    
    if latest_data:
        print(f"最新数据ID: {latest_data[0]}")
        print(f"大坝ID: {latest_data[1]}")
        print(f"时间戳: {latest_data[2]}")
        print(f"水位: {latest_data[3]}")
        print(f"压力: {latest_data[4]}")
        print(f"流量: {latest_data[5]}")
        print(f"温度: {latest_data[6]}")
        print(f"状态: {latest_data[11]}")
        
        # 构造API响应格式的数据
        response_data = {
            "latest_data": {
                "water_level": float(latest_data[3]) if latest_data[3] is not None else 0,
                "pressure": float(latest_data[4]) if latest_data[4] is not None else 0,
                "flow_rate": float(latest_data[5]) if latest_data[5] is not None else 0,
                "temperature": float(latest_data[6]) if latest_data[6] is not None else 0,
                "health_score": float(latest_data[12]) if latest_data[12] is not None else 100,
                "status": latest_data[11] if latest_data[11] else "NORMAL",
                "timestamp": latest_data[2] if latest_data[2] else ""
            }
        }
        
        print("\n格式化的数据:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
    else:
        print("没有找到数据")
    
    conn.close()

def check_table_schema():
    """检查数据库表结构"""
    conn = sqlite3.connect('cloud_data.db')
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(dam_sensor_data)")
    columns = cursor.fetchall()
    
    print("\n表结构:")
    for i, col in enumerate(columns):
        print(f"{i}: {col}")
    
    conn.close()

def insert_test_data():
    """插入测试数据"""
    conn = sqlite3.connect('cloud_data.db')
    cursor = conn.cursor()
    
    # 插入测试数据
    timestamp = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO dam_sensor_data 
        (dam_id, timestamp, water_level, pressure, flow_rate, temperature,
         displacement_x, displacement_y, displacement_z, seepage, status,
         health_score, anomalies, edge_server_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'DAM001', timestamp, 85.5, 120.5, 150.0, 7.5,
        0.01, 0.02, 0.03, 1.5, 'NORMAL', 100.0, '[]', 'EDGE001'
    ))
    
    conn.commit()
    print(f"插入测试数据成功，ID: {cursor.lastrowid}")
    conn.close()

if __name__ == "__main__":
    print("=== 检查数据库表结构 ===")
    check_table_schema()
    
    print("\n=== 获取最新数据 ===")
    get_latest_data()
    
    print("\n=== 插入测试数据 ===")
    insert_test_data()
    
    print("\n=== 再次获取最新数据 ===")
    get_latest_data() 