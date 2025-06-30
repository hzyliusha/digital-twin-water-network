"""
水网数字孪生平台云端服务
"""
import os
import json
import time
import datetime
import threading
import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import pymongo
import paho.mqtt.client as mqtt

# 添加项目根目录到系统路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG, MQTT_CONFIG, CLOUD_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("cloud_service.log")
    ]
)
logger = logging.getLogger("cloud_service")

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'water_network_twin_secret_key'
socketio = SocketIO(app)

# 连接MongoDB
try:
    mongo_client = pymongo.MongoClient(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    db = mongo_client[DB_CONFIG['db_name']]
    
    # 获取集合
    devices_collection = db[DB_CONFIG['collection_devices']]
    telemetry_collection = db[DB_CONFIG['collection_telemetry']]
    events_collection = db[DB_CONFIG['collection_events']]
    
    logger.info("成功连接到MongoDB")
except Exception as e:
    logger.error(f"连接MongoDB失败: {e}")
    db = None
    devices_collection = None
    telemetry_collection = None
    events_collection = None

# MQTT客户端设置
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT连接结果: {rc}")
    client.subscribe(MQTT_CONFIG['topic_telemetry'])
    client.subscribe(MQTT_CONFIG['topic_status'])

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.debug(f"收到消息: {msg.topic} {payload}")
        
        if msg.topic == MQTT_CONFIG['topic_telemetry']:
            # 处理遥测数据
            process_telemetry(payload)
        
        elif msg.topic == MQTT_CONFIG['topic_status']:
            # 处理状态更新
            process_status(payload)
    
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def process_telemetry(data):
    """处理遥测数据"""
    try:
        # 添加时间戳
        if 'timestamp' not in data:
            data['timestamp'] = datetime.datetime.now().isoformat()
        
        # 保存到数据库
        if telemetry_collection:
            telemetry_collection.insert_one(data)
        
        # 更新设备最新数据
        device_id = data.get('device_id')
        if device_id and devices_collection:
            # 更新设备的最新遥测数据
            devices_collection.update_one(
                {'device_id': device_id},
                {'$set': {
                    'last_telemetry': data,
                    'last_updated': datetime.datetime.now()
                }},
                upsert=True
            )
        
        # 通过WebSocket发送数据
        socketio.emit('telemetry_update', data)
        
    except Exception as e:
        logger.error(f"处理遥测数据时出错: {e}")

def process_status(data):
    """处理状态更新"""
    try:
        # 添加时间戳
        if 'timestamp' not in data:
            data['timestamp'] = datetime.datetime.now().isoformat()
        
        # 保存到数据库
        if events_collection:
            events_collection.insert_one(data)
        
        # 更新设备状态
        device_id = data.get('device_id')
        status = data.get('status')
        
        if device_id and status and devices_collection:
            # 更新设备状态
            devices_collection.update_one(
                {'device_id': device_id},
                {'$set': {
                    'status': status,
                    'last_status_update': datetime.datetime.now()
                }},
                upsert=True
            )
        
        # 通过WebSocket发送状态更新
        socketio.emit('status_update', data)
        
    except Exception as e:
        logger.error(f"处理状态更新时出错: {e}")

def cleanup_old_data():
    """清理旧数据"""
    while True:
        try:
            # 等待一天
            time.sleep(86400)
            
            # 计算保留期限
            retention_date = datetime.datetime.now() - datetime.timedelta(days=CLOUD_CONFIG['data_retention_days'])
            
            # 删除旧的遥测数据
            if telemetry_collection:
                result = telemetry_collection.delete_many({
                    'timestamp': {'$lt': retention_date.isoformat()}
                })
                logger.info(f"已删除 {result.deleted_count} 条旧的遥测数据")
            
            # 删除旧的事件数据
            if events_collection:
                result = events_collection.delete_many({
                    'timestamp': {'$lt': retention_date.isoformat()}
                })
                logger.info(f"已删除 {result.deleted_count} 条旧的事件数据")
                
        except Exception as e:
            logger.error(f"清理旧数据时出错: {e}")

# 路由定义
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    return render_template('dashboard.html')

@app.route('/devices')
def devices():
    """设备管理页面"""
    return render_template('devices.html')

# API路由
@app.route('/api/devices')
def api_devices():
    """获取所有设备"""
    try:
        if not devices_collection:
            return jsonify([])
        
        devices = list(devices_collection.find({}, {'_id': 0}))
        
        # 将最新遥测数据合并到设备信息中
        for device in devices:
            if 'last_telemetry' in device:
                # 将最新遥测数据的字段合并到设备对象中
                telemetry = device.pop('last_telemetry', {})
                for key, value in telemetry.items():
                    if key not in ['device_id', 'timestamp', 'type']:
                        device[key] = value
        
        return jsonify(devices)
    
    except Exception as e:
        logger.error(f"获取设备列表时出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/telemetry/<device_id>')
def api_telemetry(device_id):
    """获取设备遥测数据"""
    try:
        if not telemetry_collection:
            return jsonify([])
        
        # 获取查询参数
        limit = int(request.args.get('limit', 100))
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)
        
        # 构建查询条件
        query = {'device_id': device_id}
        
        if start_time:
            if 'timestamp' not in query:
                query['timestamp'] = {}
            query['timestamp']['$gte'] = start_time
        
        if end_time:
            if 'timestamp' not in query:
                query['timestamp'] = {}
            query['timestamp']['$lte'] = end_time
        
        # 查询数据
        telemetry = list(telemetry_collection.find(
            query,
            {'_id': 0}
        ).sort('timestamp', -1).limit(limit))
        
        return jsonify(telemetry)
    
    except Exception as e:
        logger.error(f"获取遥测数据时出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events')
def api_events():
    """获取事件数据"""
    try:
        if not events_collection:
            return jsonify([])
        
        # 获取查询参数
        limit = int(request.args.get('limit', 100))
        device_id = request.args.get('device_id', None)
        
        # 构建查询条件
        query = {}
        if device_id:
            query['device_id'] = device_id
        
        # 查询数据
        events = list(events_collection.find(
            query,
            {'_id': 0}
        ).sort('timestamp', -1).limit(limit))
        
        return jsonify(events)
    
    except Exception as e:
        logger.error(f"获取事件数据时出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/command', methods=['POST'])
def api_command():
    """发送命令到设备"""
    try:
        command = request.json
        
        if not command or 'device_id' not in command:
            return jsonify({'error': '无效的命令格式'}), 400
        
        # 发布命令到MQTT
        mqtt_client.publish(MQTT_CONFIG['topic_command'], json.dumps(command))
        
        return jsonify({'success': True, 'message': '命令已发送'})
    
    except Exception as e:
        logger.error(f"发送命令时出错: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    """主函数"""
    try:
        logger.info("启动水网数字孪生平台云端服务")
        
        # 连接MQTT代理
        logger.info(f"连接MQTT代理: {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
        mqtt_client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)
        
        # 启动MQTT循环
        mqtt_client.loop_start()
        
        # 启动数据清理线程
        cleanup_thread = threading.Thread(target=cleanup_old_data)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        # 启动Flask应用
        host = CLOUD_CONFIG.get('host', '0.0.0.0')
        port = CLOUD_CONFIG.get('port', 5000)
        debug = CLOUD_CONFIG.get('debug', False)
        
        logger.info(f"启动Web服务器: {host}:{port}")
        socketio.run(app, host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("接收到退出信号，正在关闭...")
    except Exception as e:
        logger.error(f"运行时出错: {e}")
    finally:
        # 停止MQTT循环
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("云端服务已关闭")

if __name__ == "__main__":
    main() 