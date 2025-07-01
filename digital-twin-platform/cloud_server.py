from flask import Flask, request, jsonify, render_template_string
import json
import sqlite3
import threading
from datetime import datetime, timedelta
import statistics
import traceback

app = Flask(__name__)

class CloudDataCenter:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """初始化云端数据库"""
        conn = sqlite3.connect('cloud_data.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # 创建传感器数据表
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
        
        # 创建分析结果表
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
                recommendations TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_batch_data(self, batch_data, edge_server_id):
        """存储批量数据"""
        conn = sqlite3.connect('cloud_data.db', check_same_thread=False)
        cursor = conn.cursor()
        
        success_count = 0
        for data in batch_data:
            try:
                # 确保sensors字段存在
                if 'sensors' not in data:
                    print(f"跳过处理数据项: 缺少sensors字段")
                    continue
                
                sensors = data['sensors']
                
                # 确保所有数据都是正确的类型
                try:
                    dam_id = data.get('dam_id', 'DAM001')
                    timestamp = data.get('timestamp', datetime.now().isoformat())
                    
                    # 确保数值字段是浮点数
                    water_level = float(sensors.get('water_level', 0))
                    pressure = float(sensors.get('pressure', 0))
                    flow_rate = float(sensors.get('flow_rate', 0))
                    temperature = float(sensors.get('temperature', 0))
                    
                    # 处理displacement字段
                    displacement = sensors.get('displacement', {'x': 0, 'y': 0, 'z': 0})
                    if not isinstance(displacement, dict):
                        displacement = {'x': 0, 'y': 0, 'z': 0}
                    
                    displacement_x = float(displacement.get('x', 0))
                    displacement_y = float(displacement.get('y', 0))
                    displacement_z = float(displacement.get('z', 0))
                    seepage = float(sensors.get('seepage', 0))
                    status = data.get('status', 'NORMAL')
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"数据类型转换错误: {e}, 数据: {data}")
                    continue
                
                # 确保健康指数是数值
                try:
                    health_score = float(data.get('health_score', 100))
                except (ValueError, TypeError):
                    health_score = 100.0
                
                # 确保异常列表是有效的JSON
                try:
                    anomalies_json = json.dumps(data.get('anomalies', []))
                except Exception:
                    anomalies_json = '[]'
                
                # 打印调试信息
                print(f"插入数据: 水位={water_level}, 压力={pressure}, 流量={flow_rate}")
                
                cursor.execute('''
                    INSERT INTO dam_sensor_data 
                    (dam_id, timestamp, water_level, pressure, flow_rate, temperature,
                     displacement_x, displacement_y, displacement_z, seepage, status,
                     health_score, anomalies, edge_server_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dam_id, timestamp, water_level, pressure, flow_rate,
                    temperature, displacement_x, displacement_y, displacement_z,
                    seepage, status, health_score, anomalies_json, edge_server_id
                ))
                success_count += 1
            except Exception as e:
                print(f"跳过处理数据项: {e}")
        
        print(f"成功存储 {success_count}/{len(batch_data)} 条数据")
        
        conn.commit()
        conn.close()
        
        # 触发数据分析
        if success_count > 0:
            self.perform_analysis()
    
    def perform_analysis(self):
        """执行大坝数据分析"""
        try:
            conn = sqlite3.connect('cloud_data.db', check_same_thread=False)
            cursor = conn.cursor()
            
            # 获取最近24小时的数据进行分析
            cursor.execute('''
                SELECT water_level, pressure, flow_rate, health_score
                FROM dam_sensor_data 
                WHERE datetime(timestamp) >= datetime('now', '-1 day')
                ORDER BY timestamp DESC
            ''')
            
            recent_data = cursor.fetchall()
            
            if recent_data and len(recent_data) > 0:
                # 计算统计指标
                water_levels = [float(row[0]) for row in recent_data if row[0] is not None]
                pressures = [float(row[1]) for row in recent_data if row[1] is not None]
                flow_rates = [float(row[2]) for row in recent_data if row[2] is not None]
                health_scores = [float(row[3]) if row[3] is not None else 100.0 for row in recent_data]
                
                if not water_levels or not pressures or not flow_rates:
                    print("警告: 没有足够的数据进行分析")
                    conn.close()
                    return
                
                avg_water_level = statistics.mean(water_levels)
                avg_pressure = statistics.mean(pressures)
                avg_flow_rate = statistics.mean(flow_rates)
                avg_health_score = statistics.mean(health_scores)
                
                # 统计异常数量
                cursor.execute('''
                    SELECT COUNT(*) FROM dam_sensor_data 
                    WHERE datetime(timestamp) >= datetime('now', '-1 day')
                    AND anomalies != '[]'
                ''')
                anomaly_count = cursor.fetchone()[0]
                
                # 评估风险等级
                risk_level = self.assess_risk(avg_water_level, avg_pressure, 
                                            avg_health_score, anomaly_count)
                
                # 生成建议
                recommendations = self.generate_recommendations(
                    avg_water_level, avg_pressure, avg_flow_rate, anomaly_count)
                
                # 确保recommendations是列表类型
                if not isinstance(recommendations, list):
                    recommendations = [str(recommendations)]
                
                # 将空字符串替换为默认建议
                if not recommendations or (len(recommendations) == 1 and not recommendations[0]):
                    recommendations = ["大坝运行状态良好，继续常规监测"]
                
                # 将每个建议确保是字符串类型
                recommendations = [str(rec) for rec in recommendations]
                
                # 打印调试信息
                print(f"生成的建议: {recommendations}")
                
                # 确保生成的JSON是有效的
                try:
                    recommendations_json = json.dumps(recommendations)
                    print(f"建议JSON: {recommendations_json}")
                except Exception as e:
                    print(f"JSON序列化失败: {e}, 使用默认建议")
                    recommendations_json = json.dumps(["大坝运行状态良好，继续常规监测"])
                
                # 保存分析结果
                cursor.execute('''
                    INSERT INTO dam_analysis 
                    (dam_id, analysis_time, avg_water_level, avg_pressure, 
                     avg_flow_rate, avg_health_score, total_anomalies, 
                     risk_level, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'DAM001', datetime.now().isoformat(),
                    avg_water_level, avg_pressure, avg_flow_rate,
                    avg_health_score, anomaly_count, risk_level,
                    recommendations_json
                ))
                
                conn.commit()
                print(f"分析完成: 风险等级={risk_level}, 建议数量={len(recommendations)}")
            else:
                print("没有足够的数据进行分析")
            
            conn.close()
        except Exception as e:
            print(f"分析过程中出错: {e}")
            traceback.print_exc()
    
    def assess_risk(self, water_level, pressure, health_score, anomaly_count):
        """评估风险等级"""
        if water_level > 95 or pressure > 160 or health_score < 60 or anomaly_count > 10:
            return "HIGH"
        elif water_level > 90 or pressure > 140 or health_score < 80 or anomaly_count > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_recommendations(self, water_level, pressure, flow_rate, anomalies):
        """生成运维建议"""
        recommendations = []
        
        try:
            if water_level > 90:
                recommendations.append("建议监控水位变化，必要时进行泄洪")
            if pressure > 140:
                recommendations.append("建议检查坝体结构，关注压力变化趋势")
            if flow_rate > 200:
                recommendations.append("建议检查泄洪设施，确保正常运行")
            if anomalies > 5:
                recommendations.append("检测到多项异常，建议进行全面设备检查")
            
            if not recommendations:
                recommendations.append("大坝运行状态良好，继续常规监测")
                
            # 确保所有建议都是字符串类型
            recommendations = [str(rec) for rec in recommendations if rec]
            
            # 如果列表为空，添加默认建议
            if not recommendations:
                recommendations.append("大坝运行状态良好，继续常规监测")
            
            print(f"生成建议: {recommendations}")
            return recommendations
        except Exception as e:
            print(f"生成建议时出错: {e}")
            return ["系统运行正常，继续监控"]

cloud_dc = CloudDataCenter()

# 添加一个简单的健康检查路由
@app.route('/')
def health_check():
    return jsonify({"status": "ok", "message": "云数据中心运行正常"}), 200

@app.route('/receive_edge_data', methods=['POST'])
def receive_edge_data():
    """接收边缘服务器数据"""
    try:
        data = request.json
        batch_data = data['batch_data']
        edge_server_id = data['edge_server_id']
        
        print(f"接收到边缘数据批次: {len(batch_data)} 条记录")
        
        # 处理数据，移除可能导致错误的字段
        for item in batch_data:
            # 移除边缘处理时间戳，避免类型转换问题
            if 'processed_at_edge' in item:
                item.pop('processed_at_edge', None)
            
            # 确保所有必要字段都存在
            if 'sensors' not in item:
                print(f"警告: 数据项缺少sensors字段: {item}")
                continue
                
            # 确保所有必要的传感器数据存在
            sensors = item['sensors']
            required_fields = ['water_level', 'pressure', 'flow_rate', 'temperature', 'displacement', 'seepage']
            for field in required_fields:
                if field not in sensors:
                    if field == 'displacement':
                        sensors[field] = {'x': 0, 'y': 0, 'z': 0}
                    else:
                        sensors[field] = 0
            
            # 确保状态字段存在
            if 'status' not in item:
                item['status'] = 'NORMAL'
        
        # 存储数据并进行分析
        try:
            cloud_dc.store_batch_data(batch_data, edge_server_id)
            print(f"成功存储边缘数据: {len(batch_data)} 条记录")
        except Exception as e:
            print(f"数据存储错误: {e}")
            # 即使存储失败，也返回成功，避免重复发送
            return jsonify({"status": "partial", "message": f"部分数据处理失败: {e}"}), 200
        
        return jsonify({"status": "success", "message": f"成功处理 {len(batch_data)} 条数据"}), 200
    
    except Exception as e:
        print(f"云端数据处理错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """数据可视化仪表板"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/dashboard_data')
def get_dashboard_data():
    """获取仪表板数据"""
    # 添加CORS头
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    try:
        print("\n=== 开始获取仪表盘数据 ===")
        conn = sqlite3.connect('cloud_data.db')
        cursor = conn.cursor()
        
        # 获取最新数据 - 使用ID排序而不是时间戳
        print("尝试获取最新传感器数据...")
        cursor.execute('''
            SELECT * FROM dam_sensor_data 
            ORDER BY id DESC LIMIT 1
        ''')
        latest_data = cursor.fetchone()
        print(f"获取到最新数据: {latest_data}")
        if latest_data:
            print(f"数据类型: {[type(x) for x in latest_data]}")
        
        # 获取最新分析结果
        print("尝试获取最新分析结果...")
        cursor.execute('''
            SELECT * FROM dam_analysis 
            ORDER BY id DESC LIMIT 1
        ''')
        latest_analysis = cursor.fetchone()
        print(f"获取到最新分析: {latest_analysis}")
        
        # 获取24小时历史数据
        print("尝试获取历史数据...")
        cursor.execute('''
            SELECT timestamp, water_level, pressure, flow_rate, health_score
            FROM dam_sensor_data 
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
            ORDER BY timestamp ASC
            LIMIT 100
        ''')
        history_data = cursor.fetchall()
        print(f"获取到历史数据: {len(history_data)} 条记录")
        
        conn.close()
        
        # 构造响应数据
        if latest_data:
            try:
                print("开始构造响应数据...")
                # 使用正确的索引
                # id=0, dam_id=1, timestamp=2, water_level=3, pressure=4, flow_rate=5, temperature=6
                # displacement_x=7, displacement_y=8, displacement_z=9, seepage=10, status=11
                # health_score=12, anomalies=13, edge_server_id=14, created_at=15
                response_data = {
                    "latest_data": {
                        "water_level": float(latest_data[3]) if latest_data[3] is not None else 0,
                        "pressure": float(latest_data[4]) if latest_data[4] is not None else 0,
                        "flow_rate": float(latest_data[5]) if latest_data[5] is not None else 0,
                        "temperature": float(latest_data[6]) if latest_data[6] is not None else 0,
                        "health_score": float(latest_data[12]) if latest_data[12] is not None else 100,
                        "status": latest_data[11] if latest_data[11] else "NORMAL",
                        "timestamp": latest_data[2] if latest_data[2] else ""
                    },
                    "analysis": {
                        "risk_level": latest_analysis[7] if latest_analysis and len(latest_analysis) > 7 else "LOW",
                        "recommendations": []
                    },
                    "history": []
                }
                
                # 安全解析recommendations JSON
                if latest_analysis and len(latest_analysis) > 8 and latest_analysis[8]:
                    try:
                        # 检查是否为空字符串或None
                        if latest_analysis[8] and latest_analysis[8].strip():
                            recommendations = json.loads(latest_analysis[8])
                            response_data["analysis"]["recommendations"] = recommendations
                        else:
                            response_data["analysis"]["recommendations"] = ["大坝运行状态良好，继续常规监测"]
                    except json.JSONDecodeError as e:
                        print(f"解析recommendations JSON失败: {e}, 原始数据: {latest_analysis[8]}")
                        # 如果无法解析，尝试将字符串作为单个建议添加
                        if isinstance(latest_analysis[8], str):
                            response_data["analysis"]["recommendations"] = [latest_analysis[8]]
                        else:
                            response_data["analysis"]["recommendations"] = ["无法解析分析建议，请联系系统管理员"]
                
                # 添加历史数据
                for row in history_data:
                    try:
                        history_item = {
                            "timestamp": row[0],
                            "water_level": float(row[1]) if row[1] is not None else 0,
                            "pressure": float(row[2]) if row[2] is not None else 0,
                            "flow_rate": float(row[3]) if row[3] is not None else 0,
                            "health_score": float(row[4]) if row[4] is not None else 100.0
                        }
                        response_data["history"].append(history_item)
                    except (ValueError, TypeError) as e:
                        print(f"跳过历史数据项: {e}, 数据: {row}")
                
                print("响应数据构造成功")
                print(f"最新数据: {json.dumps(response_data['latest_data'], indent=2)}")
                print(f"历史数据条数: {len(response_data['history'])}")
            except Exception as e:
                print(f"构造响应数据时出错: {e}")
                import traceback
                traceback.print_exc()
                response_data = {
                    "latest_data": {
                        "water_level": 0,
                        "pressure": 0,
                        "flow_rate": 0,
                        "temperature": 0,
                        "health_score": 100,
                        "status": "ERROR",
                        "timestamp": ""
                    },
                    "analysis": {
                        "risk_level": "UNKNOWN",
                        "recommendations": ["数据处理错误，请检查服务器日志"]
                    },
                    "history": []
                }
        else:
            print("没有找到最新数据，返回默认值")
            response_data = {
                "latest_data": {
                    "water_level": 0,
                    "pressure": 0,
                    "flow_rate": 0,
                    "temperature": 0,
                    "health_score": 100,
                    "status": "NORMAL",
                    "timestamp": ""
                },
                "analysis": {
                    "risk_level": "LOW",
                    "recommendations": []
                },
                "history": []
            }
    except Exception as e:
        print(f"获取仪表盘数据错误: {e}")
        import traceback
        traceback.print_exc()
        response_data = {
            "latest_data": {
                "water_level": 0,
                "pressure": 0,
                "flow_rate": 0,
                "temperature": 0,
                "health_score": 100,
                "status": "ERROR",
                "timestamp": ""
            },
            "analysis": {
                "risk_level": "UNKNOWN",
                "recommendations": ["系统数据获取错误，请检查服务状态"]
            },
            "history": []
        }
    
    print("=== 完成获取仪表盘数据 ===\n")
    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/test', methods=['GET'])
def api_test():
    """简单的API测试端点"""
    response = jsonify({
        "status": "ok",
        "message": "API正常工作",
        "timestamp": datetime.now().isoformat()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/latest_data')
def get_latest_data():
    """获取最新数据的简化API"""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    try:
        conn = sqlite3.connect('cloud_data.db')
        cursor = conn.cursor()
        
        # 获取最新数据
        cursor.execute('''
            SELECT * FROM dam_sensor_data 
            ORDER BY id DESC LIMIT 1
        ''')
        latest_data = cursor.fetchone()
        conn.close()
        
        if latest_data:
            response_data = {
                "id": latest_data[0],
                "dam_id": latest_data[1],
                "timestamp": latest_data[2],
                "water_level": float(latest_data[3]) if latest_data[3] is not None else 0,
                "pressure": float(latest_data[4]) if latest_data[4] is not None else 0,
                "flow_rate": float(latest_data[5]) if latest_data[5] is not None else 0,
                "temperature": float(latest_data[6]) if latest_data[6] is not None else 0,
                "status": latest_data[11] if latest_data[11] else "NORMAL"
            }
        else:
            response_data = {
                "error": "No data found"
            }
    except Exception as e:
        print(f"获取最新数据错误: {e}")
        response_data = {
            "error": str(e)
        }
    
    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/history_data')
def get_history_data():
    """获取历史数据的API"""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    try:
        conn = sqlite3.connect('cloud_data.db')
        cursor = conn.cursor()
        
        # 获取24小时历史数据
        cursor.execute('''
            SELECT id, timestamp, water_level, pressure, flow_rate, temperature, status
            FROM dam_sensor_data 
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
            ORDER BY id ASC
            LIMIT 100
        ''')
        history_data = cursor.fetchall()
        conn.close()
        
        if history_data:
            response_data = []
            for row in history_data:
                try:
                    item = {
                        "id": row[0],
                        "timestamp": row[1],
                        "water_level": float(row[2]) if row[2] is not None else 0,
                        "pressure": float(row[3]) if row[3] is not None else 0,
                        "flow_rate": float(row[4]) if row[4] is not None else 0,
                        "temperature": float(row[5]) if row[5] is not None else 0,
                        "status": row[6] if row[6] else "NORMAL"
                    }
                    response_data.append(item)
                except (ValueError, TypeError) as e:
                    print(f"跳过历史数据项: {e}, 数据: {row}")
        else:
            response_data = []
    except Exception as e:
        print(f"获取历史数据错误: {e}")
        response_data = []
    
    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 仪表板HTML模板
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>大坝数字孪生系统仪表板</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f2f5;
            color: #333;
        }
        .header {
            background-color: #1e88e5;
            color: white;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            grid-gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .card-title {
            margin-top: 0;
            color: #1e88e5;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            grid-gap: 15px;
        }
        .metric {
            text-align: center;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
        .chart-container {
            height: 300px;
            margin-top: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 5px;
            background-color: #ccc;
        }
        .status-indicator.normal {
            background-color: #4caf50;
        }
        .status-indicator.warning {
            background-color: #ff9800;
        }
        .status-indicator.danger {
            background-color: #f44336;
        }
        .risk-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 5px;
            background-color: #ccc;
        }
        .risk-indicator.low {
            background-color: #4caf50;
        }
        .risk-indicator.medium {
            background-color: #ff9800;
        }
        .risk-indicator.high {
            background-color: #f44336;
        }
        .footer {
            text-align: center;
            padding: 15px;
            color: #666;
            font-size: 0.8em;
            border-top: 1px solid #eee;
            margin-top: 20px;
        }
        .status-normal {
            color: #4caf50;
        }
        .status-warning {
            color: #ff9800;
        }
        .status-danger {
            color: #f44336;
        }
        #error-container {
            background-color: #ffebee;
            color: #c62828;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: none;
        }
        #last-update {
            text-align: right;
            color: #666;
            font-size: 0.8em;
            margin-top: 20px;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>大坝数字孪生系统仪表板</h1>
    </div>
    
    <div class="container">
        <div id="error-container">
            <p id="error-message">数据加载失败，请检查网络连接。</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2 class="card-title">实时监测数据</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-label">水位</div>
                        <div class="metric-value" id="water-level">--</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">压力</div>
                        <div class="metric-value" id="pressure">--</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">流量</div>
                        <div class="metric-value" id="flow-rate">--</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">温度</div>
                        <div class="metric-value" id="temperature">--</div>
                    </div>
                </div>
                <div style="margin-top: 20px;">
                    <div style="display: flex; align-items: center;">
                        <span>状态: </span>
                        <span class="status-indicator" id="status-indicator"></span>
                        <span id="status-text">未知</span>
                    </div>
                </div>
                <div id="last-update">最后更新: --</div>
            </div>
            
            <div class="card">
                <h2 class="card-title">风险评估</h2>
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; align-items: center;">
                        <span>风险等级: </span>
                        <span class="risk-indicator" id="risk-indicator"></span>
                        <span id="risk-text">未知</span>
                    </div>
                </div>
                <h3>运维建议</h3>
                <ul id="recommendations-list">
                    <li>加载中...</li>
                </ul>
            </div>
        </div>
        
        <div class="card">
            <h2 class="card-title">历史趋势</h2>
            <div class="chart-container">
                <canvas id="history-chart"></canvas>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>大坝数字孪生系统 &copy; 2025</p>
    </div>
    
    <script>
        // 图表对象
        let historyChart = null;
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            console.log("仪表盘初始化...");
            initChart();
            updateDashboard();
            
            // 每10秒更新一次数据
            setInterval(updateDashboard, 10000);
        });
        
        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('history-chart').getContext('2d');
            historyChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: '水位 (m)',
                            data: [],
                            borderColor: '#1e88e5',
                            backgroundColor: 'rgba(30, 136, 229, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: '压力 (kPa)',
                            data: [],
                            borderColor: '#43a047',
                            backgroundColor: 'rgba(67, 160, 71, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: '流量 (m³/s)',
                            data: [],
                            borderColor: '#fb8c00',
                            backgroundColor: 'rgba(251, 140, 0, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '时间'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '数值'
                            }
                        }
                    }
                }
            });
        }
        
        // 更新图表数据
        function updateCharts(historyData) {
            if (!historyChart || !historyData || historyData.length === 0) {
                console.warn("无法更新图表：图表未初始化或无历史数据");
                return;
            }
            
            // 处理时间格式
            const labels = historyData.map(item => {
                const date = new Date(item.timestamp);
                return date.toLocaleTimeString();
            });
            
            // 提取数据
            const waterLevelData = historyData.map(item => item.water_level);
            const pressureData = historyData.map(item => item.pressure);
            const flowRateData = historyData.map(item => item.flow_rate);
            
            // 更新图表数据
            historyChart.data.labels = labels;
            historyChart.data.datasets[0].data = waterLevelData;
            historyChart.data.datasets[1].data = pressureData;
            historyChart.data.datasets[2].data = flowRateData;
            
            // 更新图表
            historyChart.update();
        }
        
        // 仪表盘数据更新
        function updateDashboard() {
            console.log("更新仪表盘数据...");
            
            // 先尝试获取最新数据
            fetch('/api/latest_data')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('网络响应异常');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("获取到最新数据:", data);
                    
                    // 更新最新数据显示
                    document.getElementById('water-level').textContent = data.water_level ? data.water_level.toFixed(2) + 'm' : '--';
                    document.getElementById('pressure').textContent = data.pressure ? data.pressure.toFixed(2) + 'kPa' : '--';
                    document.getElementById('flow-rate').textContent = data.flow_rate ? data.flow_rate.toFixed(2) + 'm³/s' : '--';
                    document.getElementById('temperature').textContent = data.temperature ? data.temperature.toFixed(2) + '°C' : '--';
                    
                    // 更新状态指示灯
                    const statusIndicator = document.getElementById('status-indicator');
                    const statusText = document.getElementById('status-text');
                    
                    if (data.status === 'NORMAL') {
                        statusIndicator.className = 'status-indicator normal';
                        statusText.textContent = '正常';
                    } else if (data.status === 'WARNING') {
                        statusIndicator.className = 'status-indicator warning';
                        statusText.textContent = '警告';
                    } else if (data.status === 'DANGER') {
                        statusIndicator.className = 'status-indicator danger';
                        statusText.textContent = '危险';
                    } else {
                        statusIndicator.className = 'status-indicator';
                        statusText.textContent = '未知';
                    }
                    
                    // 更新时间戳
                    const timestamp = data.timestamp ? new Date(data.timestamp).toLocaleString() : '--';
                    document.getElementById('last-update').textContent = '最后更新: ' + timestamp;
                    
                    // 获取历史数据
                    return fetch('/api/history_data');
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('获取历史数据失败');
                    }
                    return response.json();
                })
                .then(historyData => {
                    console.log(`获取到 ${historyData.length} 条历史数据`);
                    
                    // 更新历史数据图表
                    if (historyData && historyData.length > 0) {
                        updateCharts(historyData);
                    }
                    
                    // 获取完整的仪表盘数据（包括分析结果）
                    return fetch('/api/dashboard_data');
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('获取完整仪表盘数据失败');
                    }
                    return response.json();
                })
                .then(dashboardData => {
                    console.log("获取到完整仪表盘数据");
                    
                    // 更新分析结果
                    if (dashboardData.analysis) {
                        const riskLevel = dashboardData.analysis.risk_level || 'UNKNOWN';
                        const riskIndicator = document.getElementById('risk-indicator');
                        const riskText = document.getElementById('risk-text');
                        
                        if (riskLevel === 'LOW') {
                            riskIndicator.className = 'risk-indicator low';
                            riskText.textContent = '低风险';
                        } else if (riskLevel === 'MEDIUM') {
                            riskIndicator.className = 'risk-indicator medium';
                            riskText.textContent = '中风险';
                        } else if (riskLevel === 'HIGH') {
                            riskIndicator.className = 'risk-indicator high';
                            riskText.textContent = '高风险';
                        } else {
                            riskIndicator.className = 'risk-indicator';
                            riskText.textContent = '未知';
                        }
                        
                        // 更新建议列表
                        const recommendationsList = document.getElementById('recommendations-list');
                        recommendationsList.innerHTML = '';
                        
                        if (dashboardData.analysis.recommendations && dashboardData.analysis.recommendations.length > 0) {
                            dashboardData.analysis.recommendations.forEach(rec => {
                                const li = document.createElement('li');
                                li.textContent = rec;
                                recommendationsList.appendChild(li);
                            });
                        } else {
                            const li = document.createElement('li');
                            li.textContent = '无建议';
                            recommendationsList.appendChild(li);
                        }
                    }
                })
                .catch(error => {
                    console.error('获取数据错误:', error);
                    // 显示错误信息
                    document.getElementById('error-message').textContent = '数据获取失败: ' + error.message;
                    document.getElementById('error-container').style.display = 'block';
                    
                    // 5秒后隐藏错误信息
                    setTimeout(() => {
                        document.getElementById('error-container').style.display = 'none';
                    }, 5000);
                });
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("云数据中心启动中...")
    app.run(host='0.0.0.0', port=8002, debug=False) 