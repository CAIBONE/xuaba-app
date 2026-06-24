#!/usr/bin/env python3
"""
429 错误重试包装器
检测到 429 错误时，每 5 分钟重试一次
"""
import requests
import time
import sys
from functools import wraps

def retry_on_429(max_retries=10, delay=300):
    """
    429 错误重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试间隔（秒），默认 5 分钟
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)

                    # 检查是否是 requests 响应对象
                    if hasattr(result, 'status_code'):
                        if result.status_code == 429:
                            if attempt < max_retries - 1:
                                print(f"\n⚠ 遇到 429 限流错误，等待 {delay} 秒后重试...")
                                print(f"  重试次数: {attempt + 1}/{max_retries}")
                                time.sleep(delay)
                                continue
                            else:
                                print(f"\n✗ 达到最大重试次数 ({max_retries})，放弃")
                                return result
                        else:
                            return result
                    else:
                        return result

                except requests.exceptions.RequestException as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        print(f"\n⚠ 遇到 429 限流错误，等待 {delay} 秒后重试...")
                        print(f"  重试次数: {attempt + 1}/{max_retries}")
                        time.sleep(delay)
                        continue
                    else:
                        raise

            return result
        return wrapper
    return decorator

@retry_on_429(max_retries=10, delay=300)
def make_request(method, url, **kwargs):
    """发送 HTTP 请求，自动处理 429 错误"""
    if method.upper() == 'GET':
        return requests.get(url, **kwargs)
    elif method.upper() == 'POST':
        return requests.post(url, **kwargs)
    elif method.upper() == 'PUT':
        return requests.put(url, **kwargs)
    elif method.upper() == 'DELETE':
        return requests.delete(url, **kwargs)
    else:
        raise ValueError(f"不支持的 HTTP 方法: {method}")

if __name__ == "__main__":
    # 测试示例
    print("测试 429 重试机制...")
    print("请在另一个终端模拟 429 错误来测试此功能")

    # 示例：发送请求
    response = make_request('GET', 'http://127.0.0.1:8000/health')
    print(f"响应状态码: {response.status_code}")
