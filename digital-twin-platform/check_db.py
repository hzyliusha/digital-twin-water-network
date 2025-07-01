import sqlite3
import json

def check_cloud_db():
    """检查云数据库的结构和内容"""
    print("=== 检查云数据库 ===")
    conn = sqlite3.connect('cloud_data.db')
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(dam_sensor_data)")
    columns = cursor.fetchall()
    print("\n表结构 dam_sensor_data:")
    for i, col in enumerate(columns):
        print(f"{i}: {col}")
    
    # 检查数据
    cursor.execute("SELECT COUNT(*) FROM dam_sensor_data")
    count = cursor.fetchone()[0]
    print(f"\n总记录数: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM dam_sensor_data ORDER BY timestamp DESC LIMIT 1")
        latest = cursor.fetchone()
        print("\n最新记录:")
        for i, col in enumerate(columns):
            col_name = col[1]
            value = latest[i]
            print(f"{col_name}: {value}")
    
    conn.close()

def check_edge_db():
    """检查边缘数据库的结构和内容"""
    print("\n=== 检查边缘数据库 ===")
    conn = sqlite3.connect('edge_data.db')
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(sensor_data)")
    columns = cursor.fetchall()
    print("\n表结构 sensor_data:")
    for i, col in enumerate(columns):
        print(f"{i}: {col}")
    
    # 检查数据
    cursor.execute("SELECT COUNT(*) FROM sensor_data")
    count = cursor.fetchone()[0]
    print(f"\n总记录数: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
        latest = cursor.fetchone()
        print("\n最新记录:")
        for i, col in enumerate(columns):
            col_name = col[1]
            value = latest[i]
            print(f"{col_name}: {value}")
    
    conn.close()

if __name__ == "__main__":
    check_cloud_db()
    check_edge_db() 