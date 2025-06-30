"""
配置文件，包含水网数字孪生系统各组件的配置参数
"""

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'db_name': 'water_network_twin',
    'collection_devices': 'devices',
    'collection_telemetry': 'telemetry',
    'collection_events': 'events'
}

# MQTT配置
MQTT_CONFIG = {
    'broker': 'localhost',
    'port': 1883,
    'topic_telemetry': 'wn/telemetry',
    'topic_command': 'wn/command',
    'topic_status': 'wn/status',
    'qos': 1
}

# 云端服务配置
CLOUD_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'data_retention_days': 30
}

# 边缘节点配置
EDGE_CONFIG = {
    'id': 'edge-001',
    'name': '水网边缘节点1',
    'location': '泵站A',
    'buffer_size': 1000,
    'processing_interval': 5,  # 数据处理间隔(秒)
    'cloud_sync_interval': 60,  # 云端同步间隔(秒)
    'local_storage_path': './edge/data'
}

# 设备配置
DEVICE_TYPES = {
    'water_sensor': {
        'attributes': ['flow_rate', 'pressure', 'water_quality', 'temperature'],
        'sampling_rate': 1,  # 采样率(秒)
        'thresholds': {
            'flow_rate': {'min': 0, 'max': 1000},  # 流量(L/min)
            'pressure': {'min': 0, 'max': 10},     # 压力(MPa)
            'water_quality': {'min': 0, 'max': 100},  # 水质指数
            'temperature': {'min': 0, 'max': 40}   # 温度(°C)
        }
    },
    'valve': {
        'attributes': ['status', 'opening', 'mode'],
        'control_modes': ['auto', 'manual'],
        'status_options': ['open', 'closed', 'partially_open']
    },
    'pump': {
        'attributes': ['status', 'power', 'mode', 'rpm'],
        'control_modes': ['auto', 'manual'],
        'status_options': ['on', 'off', 'standby']
    }
} 