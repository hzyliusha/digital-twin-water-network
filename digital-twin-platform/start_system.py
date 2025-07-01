import subprocess
import time
import threading
import sys
import os

def start_service(name, script_path, port):
    """启动服务"""
    print(f"正在启动 {name}...")
    try:
        process = subprocess.Popen([sys.executable, script_path])
        print(f"{name} 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"启动 {name} 失败: {e}")
        return None

def main():
    """主启动函数"""
    print("=== 大坝数字孪生系统启动 ===")
    
    processes = []
    
    # 检查Python依赖
    required_packages = ['flask', 'requests', 'sqlite3']
    print("检查依赖包...")
    
    # 启动云数据中心
    print("\n1. 启动云数据中心...")
    cloud_process = start_service("云数据中心", "cloud_server.py", 8002)
    if cloud_process:
        processes.append(cloud_process)
    
    time.sleep(3)  # 等待云服务启动
    
    # 启动边缘服务器
    print("\n2. 启动边缘服务器...")
    edge_process = start_service("边缘服务器", "edge_server.py", 8001)
    if edge_process:
        processes.append(edge_process)
    
    time.sleep(3)  # 等待边缘服务启动
    
    # 启动传感器模拟器
    print("\n3. 启动传感器模拟器...")
    sensor_process = start_service("传感器模拟器", "dam_sensors.py", None)
    if sensor_process:
        processes.append(sensor_process)
    
    print("\n=== 系统启动完成 ===")
    print("访问地址:")
    print("- 云数据中心仪表板: http://localhost:8002/dashboard")
    print("- 边缘服务器状态: http://localhost:8001/status")
    print("- 按 Ctrl+C 停止系统")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止系统...")
        for process in processes:
            if process:
                process.terminate()
        print("系统已停止")

if __name__ == "__main__":
    main() 