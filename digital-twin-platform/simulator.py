"""
大坝数字孪生系统 - 系统概览

这个文件提供了系统的概述，并指导用户如何运行各个组件。
实际的实现代码分布在各个独立的Python文件中。
"""

import os
import sys

def print_system_overview():
    """打印系统概述"""
    print("""
=== 大坝数字孪生系统概览 ===

系统架构:
[大坝传感器] -> [无线网络] -> [边缘服务器] -> [云数据中心] -> [可视化系统]

主要组件:
1. 传感器模拟器 (dam_sensors.py): 模拟大坝上的各类传感器数据
2. 边缘服务器 (edge_server.py): 接收传感器数据，进行初步处理并转发到云端
3. 云数据中心 (cloud_server.py): 存储和分析数据，提供可视化界面
4. 系统启动脚本 (start_system.py): 一键启动整个系统
5. 数据库初始化脚本 (init_database.py): 初始化所需的数据库
6. 配置文件 (config.json): 系统配置参数

使用方法:
1. 安装依赖: python install_requirements.py
2. 初始化数据库: python init_database.py
3. 启动系统: python start_system.py

访问系统:
- 可视化仪表板: http://localhost:8002/dashboard
- 边缘服务器状态: http://localhost:8001/status
""")

def check_files():
    """检查所需文件是否存在"""
    required_files = [
        "dam_sensors.py",
        "edge_server.py",
        "cloud_server.py",
        "start_system.py",
        "init_database.py",
        "config.json",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("警告: 以下文件缺失:")
        for file in missing_files:
            print(f"- {file}")
        print("\n请确保所有组件文件都已创建。")
    else:
        print("所有系统组件文件已就绪。")

if __name__ == "__main__":
    print_system_overview()
    print("\n正在检查系统文件...")
    check_files()
    
    print("\n要启动系统，请运行: python start_system.py")