import requests
import json

def test_latest_data_api():
    """测试最新数据API"""
    print("正在测试最新数据API...")
    try:
        response = requests.get('http://localhost:8002/api/latest_data')
        print(f"API状态码: {response.status_code}")
        
        # 打印完整响应内容
        print("\n=== 完整API响应 ===")
        print(response.text)
        
        # 解析响应数据
        try:
            data = response.json()
            print("\n=== 解析后的API响应数据 ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("API响应不是有效的JSON格式")
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保服务器已启动")
    except Exception as e:
        print(f"测试过程中出错: {e}")

if __name__ == "__main__":
    test_latest_data_api() 