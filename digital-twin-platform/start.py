"""
水网数字孪生平台启动脚本
"""
import os
import sys
import time
import argparse
import subprocess
import threading
import signal
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("startup")

# 进程列表
processes = []

def start_mqtt_broker():
    """启动MQTT代理"""
    try:
        # 检查是否已安装Mosquitto
        if sys.platform == 'win32':
            # Windows
            mosquitto_cmd = 'mosquitto'
        else:
            # Linux/Mac
            mosquitto_cmd = 'mosquitto'
        
        logger.info("启动MQTT代理...")
        process = subprocess.Popen(
            [mosquitto_cmd, '-v'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(('mqtt_broker', process))
        
        # 等待MQTT代理启动
        time.sleep(2)
        
        if process.poll() is not None:
            logger.error("MQTT代理启动失败")
            stderr = process.stderr.read()
            logger.error(f"错误信息: {stderr}")
            logger.warning("请确保已安装Mosquitto MQTT代理")
            logger.info("您可以手动启动MQTT代理，或使用在线MQTT服务")
            return False
        
        logger.info("MQTT代理启动成功")
        return True
    
    except FileNotFoundError:
        logger.error("未找到Mosquitto MQTT代理")
        logger.warning("请安装Mosquitto MQTT代理，或使用在线MQTT服务")
        logger.info("您可以从 https://mosquitto.org/download/ 下载安装")
        return False
    
    except Exception as e:
        logger.error(f"启动MQTT代理时出错: {e}")
        return False

def start_cloud_service():
    """启动云端服务"""
    try:
        logger.info("启动水网云端服务...")
        process = subprocess.Popen(
            [sys.executable, 'cloud/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(('cloud_service', process))
        
        # 等待云端服务启动
        time.sleep(2)
        
        if process.poll() is not None:
            logger.error("云端服务启动失败")
            stderr = process.stderr.read()
            logger.error(f"错误信息: {stderr}")
            return False
        
        logger.info("云端服务启动成功")
        return True
    
    except Exception as e:
        logger.error(f"启动云端服务时出错: {e}")
        return False

def start_edge_node():
    """启动边缘节点"""
    try:
        logger.info("启动水网边缘节点...")
        process = subprocess.Popen(
            [sys.executable, 'edge/edge_node.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(('edge_node', process))
        
        # 等待边缘节点启动
        time.sleep(2)
        
        if process.poll() is not None:
            logger.error("边缘节点启动失败")
            stderr = process.stderr.read()
            logger.error(f"错误信息: {stderr}")
            return False
        
        logger.info("边缘节点启动成功")
        return True
    
    except Exception as e:
        logger.error(f"启动边缘节点时出错: {e}")
        return False

def start_device_simulator(sensors=3, valves=2, pumps=2):
    """启动设备模拟器"""
    try:
        logger.info(f"启动水网设备模拟器 (水质传感器: {sensors}, 阀门: {valves}, 水泵: {pumps})...")
        process = subprocess.Popen(
            [
                sys.executable, 'device/device_simulator.py',
                '--sensors', str(sensors),
                '--valves', str(valves),
                '--pumps', str(pumps)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(('device_simulator', process))
        
        # 等待设备模拟器启动
        time.sleep(2)
        
        if process.poll() is not None:
            logger.error("设备模拟器启动失败")
            stderr = process.stderr.read()
            logger.error(f"错误信息: {stderr}")
            return False
        
        logger.info("设备模拟器启动成功")
        return True
    
    except Exception as e:
        logger.error(f"启动设备模拟器时出错: {e}")
        return False

def log_reader(name, process):
    """读取进程日志"""
    while process.poll() is None:
        line = process.stdout.readline()
        if line:
            logger.info(f"[{name}] {line.strip()}")
    
    # 进程结束后读取剩余输出
    remaining = process.stdout.read()
    if remaining:
        for line in remaining.splitlines():
            logger.info(f"[{name}] {line.strip()}")

def start_log_readers():
    """启动日志读取线程"""
    for name, process in processes:
        thread = threading.Thread(target=log_reader, args=(name, process))
        thread.daemon = True
        thread.start()

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，正在关闭所有组件...")
    
    # 按相反顺序关闭进程
    for name, process in reversed(processes):
        logger.info(f"正在关闭 {name}...")
        if sys.platform == 'win32':
            # Windows
            process.terminate()
        else:
            # Linux/Mac
            process.send_signal(signal.SIGTERM)
        
        # 等待进程结束
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning(f"{name} 未能正常关闭，强制终止")
            process.kill()
    
    logger.info("所有组件已关闭")
    sys.exit(0)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='水网数字孪生平台启动脚本')
    parser.add_argument('--mqtt', action='store_true', help='启动MQTT代理')
    parser.add_argument('--cloud', action='store_true', help='启动云端服务')
    parser.add_argument('--edge', action='store_true', help='启动边缘节点')
    parser.add_argument('--device', action='store_true', help='启动设备模拟器')
    parser.add_argument('--all', action='store_true', help='启动所有组件')
    parser.add_argument('--sensors', type=int, default=3, help='水质传感器数量')
    parser.add_argument('--valves', type=int, default=2, help='阀门数量')
    parser.add_argument('--pumps', type=int, default=2, help='水泵数量')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 确定要启动的组件
    start_mqtt = args.mqtt or args.all
    start_cloud = args.cloud or args.all
    start_edge = args.edge or args.all
    start_device = args.device or args.all
    
    # 如果没有指定任何组件，则启动所有组件
    if not (start_mqtt or start_cloud or start_edge or start_device):
        start_mqtt = start_cloud = start_edge = start_device = True
    
    # 启动组件
    if start_mqtt:
        if not start_mqtt_broker():
            logger.warning("MQTT代理启动失败，继续启动其他组件")
    
    if start_cloud:
        if not start_cloud_service():
            logger.error("云端服务启动失败，终止启动")
            signal_handler(None, None)
            return
    
    if start_edge:
        if not start_edge_node():
            logger.error("边缘节点启动失败，终止启动")
            signal_handler(None, None)
            return
    
    if start_device:
        if not start_device_simulator(args.sensors, args.valves, args.pumps):
            logger.error("设备模拟器启动失败，终止启动")
            signal_handler(None, None)
            return
    
    # 启动日志读取线程
    start_log_readers()
    
    logger.info("所有组件已启动，按Ctrl+C终止")
    
    # 主循环
    try:
        while True:
            # 检查所有进程是否仍在运行
            for name, process in processes:
                if process.poll() is not None:
                    logger.error(f"{name} 已意外终止，退出代码: {process.returncode}")
                    signal_handler(None, None)
                    return
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main() 