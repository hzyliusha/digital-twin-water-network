import sqlite3
import json
from datetime import datetime

def debug_get_dashboard_data():
    """调试仪表板API的数据获取逻辑"""
    print("=== 调试仪表板API ===")
    
    try:
        conn = sqlite3.connect('cloud_data.db')
        cursor = conn.cursor()
        
        # 获取最新数据
        print("\n尝试获取最新传感器数据...")
        cursor.execute('''
            SELECT * FROM dam_sensor_data 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        latest_data = cursor.fetchone()
        print(f"最新数据: {latest_data}")
        
        # 获取最新分析结果
        print("\n尝试获取最新分析结果...")
        cursor.execute('''
            SELECT * FROM dam_analysis 
            ORDER BY analysis_time DESC LIMIT 1
        ''')
        latest_analysis = cursor.fetchone()
        print(f"最新分析: {latest_analysis}")
        
        # 获取24小时历史数据
        print("\n尝试获取历史数据...")
        cursor.execute('''
            SELECT timestamp, water_level, pressure, flow_rate, health_score
            FROM dam_sensor_data 
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
            ORDER BY timestamp ASC
            LIMIT 10
        ''')
        history_data = cursor.fetchall()
        print(f"获取到 {len(history_data)} 条历史记录")
        if history_data:
            print(f"第一条历史记录: {history_data[0]}")
        
        conn.close()
        
        print("\n=== 构造响应数据 ===")
        
        if latest_data:
            # id=0, dam_id=1, timestamp=2, water_level=3, pressure=4, flow_rate=5, temperature=6
            # displacement_x=7, displacement_y=8, displacement_z=9, seepage=10, status=11
            # health_score=12, anomalies=13, edge_server_id=14, created_at=15
            try:
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
                print(f"成功构造最新数据: {json.dumps(response_data['latest_data'], indent=2)}")
            except Exception as e:
                print(f"构造最新数据时出错: {e}")
                print(f"数据类型: {[type(x) for x in latest_data]}")
        else:
            print("没有找到最新数据")
    
    except Exception as e:
        print(f"调试过程中出错: {e}")

if __name__ == "__main__":
    debug_get_dashboard_data() 