import requests
import json
import time

def test_dashboard_api():
    """测试仪表板API，验证修复是否成功"""
    print("开始测试仪表板API...")
    
    # 测试API端点 - 确保使用正确的端口
    base_url = "http://127.0.0.1:5000"
    api_url = f"{base_url}/api/dashboard_data"
    
    # 首先测试服务器是否在运行
    try:
        print(f"测试服务器健康检查: {base_url}")
        health_response = requests.get(base_url, timeout=5)
        print(f"健康检查响应: {health_response.status_code}")
    except Exception as e:
        print(f"健康检查失败: {e}")
    
    # 测试仪表板API
    try:
        print(f"请求API: {api_url}")
        response = requests.get(api_url, timeout=5)
        print(f"API响应状态码: {response.status_code}")
        
        response.raise_for_status()  # 如果响应状态码不是200，则引发异常
        
        data = response.json()
        print("\n=== API响应成功 ===")
        
        # 检查响应结构
        if "latest_data" in data and "analysis" in data and "history" in data:
            print("响应结构正确")
            
            # 检查最新数据
            latest = data["latest_data"]
            print(f"\n最新数据:")
            print(f"  水位: {latest.get('water_level')} m")
            print(f"  压力: {latest.get('pressure')} kPa")
            print(f"  流量: {latest.get('flow_rate')} m³/s")
            print(f"  温度: {latest.get('temperature')} °C")
            print(f"  健康评分: {latest.get('health_score')}")
            print(f"  状态: {latest.get('status')}")
            print(f"  时间戳: {latest.get('timestamp')}")
            
            # 检查分析数据
            analysis = data["analysis"]
            print(f"\n分析数据:")
            print(f"  风险等级: {analysis.get('risk_level')}")
            print(f"  运维建议: {json.dumps(analysis.get('recommendations'), ensure_ascii=False, indent=2)}")
            
            # 检查历史数据
            history = data["history"]
            print(f"\n历史数据: 共 {len(history)} 条记录")
            if history:
                print(f"  第一条: {history[0]}")
                if len(history) > 1:
                    print(f"  最后一条: {history[-1]}")
            
            return True
        else:
            print("响应结构不正确:")
            print(json.dumps(data, indent=2))
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"响应内容: {response.text[:500]}...")  # 只打印前500个字符
        return False
    except Exception as e:
        print(f"测试过程中出错: {e}")
        return False

if __name__ == "__main__":
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    # 执行测试
    success = test_dashboard_api()
    
    if success:
        print("\n✅ 测试通过: 仪表板API正常工作")
    else:
        print("\n❌ 测试失败: 仪表板API存在问题") 