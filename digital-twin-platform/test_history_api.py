import requests
import json

def test_history_data_api():
    """测试历史数据API"""
    print("正在测试历史数据API...")
    try:
        response = requests.get('http://localhost:8002/api/history_data')
        print(f"API状态码: {response.status_code}")
        
        # 解析响应数据
        try:
            data = response.json()
            print(f"获取到 {len(data)} 条历史记录")
            
            if data:
                print("\n=== 第一条历史记录 ===")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
                
                print("\n=== 最后一条历史记录 ===")
                print(json.dumps(data[-1], indent=2, ensure_ascii=False))
            else:
                print("没有历史数据")
        except json.JSONDecodeError:
            print("API响应不是有效的JSON格式")
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保服务器已启动")
    except Exception as e:
        print(f"测试过程中出错: {e}")

if __name__ == "__main__":
    test_history_data_api() 