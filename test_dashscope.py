"""测试 DashScope API 连接"""
import requests
import json
import sys

API_KEY = "sk-c3486a14e5e64610b8cd7caaa117d21a"
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

def test_api():
    """测试 API 调用"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "qwen3.7-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一个智能学习助手。"},
                {"role": "user", "content": "你好，请简单介绍一下自己。"}
            ]
        },
        "parameters": {
            "result_format": "message"
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            # 提取文本内容
            if "output" in result and "choices" in result["output"]:
                content = result["output"]["choices"][0]["message"]["content"]
                print(f"\nResponse:\n{content}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # 设置 UTF-8 编码
    sys.stdout.reconfigure(encoding='utf-8')

    print("Testing DashScope API connection...")
    if test_api():
        print("\nAPI connection successful!")
    else:
        print("\nAPI connection failed!")
