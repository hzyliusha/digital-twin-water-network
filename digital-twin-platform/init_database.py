import sqlite3
import json
from datetime import datetime

def init_edge_database():
    """初始化边缘数据库"""
    conn = sqlite3.connect('edge_data.db')
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
            processed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_dam_id ON sensor_data(dam_id)
    ''')
    
    conn.commit()
    conn.close()
    print("边缘数据库初始化完成")

def init_cloud_database():
    """初始化云端数据库"""
    conn = sqlite3.connect('cloud_data.db')
    cursor = conn.cursor()
    
    # 传感器数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dam_sensor_data (
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
            health_score REAL,
            anomalies TEXT,
            edge_server_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 分析结果表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dam_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dam_id TEXT,
            analysis_time TEXT,
            avg_water_level REAL,
            avg_pressure REAL,
            avg_flow_rate REAL,
            avg_health_score REAL,
            total_anomalies INTEGER,
            risk_level TEXT,
            recommendations TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 预警记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dam_id TEXT,
            alert_type TEXT,
            severity TEXT,
            message TEXT,
            triggered_at TEXT,
            resolved_at TEXT,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON dam_sensor_data(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_dam_id ON dam_sensor_data(dam_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_time ON dam_analysis(analysis_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_dam_id ON alerts(dam_id)')
    
    conn.commit()
    conn.close()
    print("云端数据库初始化完成")

if __name__ == "__main__":
    print("正在初始化数据库...")
    init_edge_database()
    init_cloud_database()
    print("数据库初始化完成!") 