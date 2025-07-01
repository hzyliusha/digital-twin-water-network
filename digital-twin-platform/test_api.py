import requests
import json
from datetime import datetime

def test_api():
    """测试API是否正常工作"""
    print("正在测试API...")
    try:
        # 测试获取仪表板数据API
        response = requests.get('http://localhost:8002/api/dashboard_data')
        print(f"API状态码: {response.status_code}")
        
        # 打印完整响应内容
        print("\n=== 完整API响应 ===")
        print(response.text)
        
        # 解析响应数据
        try:
            data = response.json()
            print("\n=== 解析后的API响应数据 ===")
            print("最新数据:", json.dumps(data.get('latest_data', {}), indent=2, ensure_ascii=False))
            print("分析结果:", json.dumps(data.get('analysis', {}), indent=2, ensure_ascii=False))
            print("历史数据条数:", len(data.get('history', [])))
            
            if data['history']:
                print(f"第一条历史记录: {json.dumps(data['history'][0], ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            print("API响应不是有效的JSON格式")
        
        # 测试测试API
        print("\n正在测试测试API...")
        test_response = requests.get('http://localhost:8002/api/test')
        print(f"API状态码: {test_response.status_code}")
        print("测试API响应:", json.dumps(test_response.json(), indent=2, ensure_ascii=False))
        
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保服务器已启动")
    except Exception as e:
        print(f"测试过程中出错: {e}")

if __name__ == "__main__":
    test_api() 