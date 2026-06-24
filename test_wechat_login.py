"""测试微信登录"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_wechat_login():
    """测试微信登录"""
    print("=" * 70)
    print("测试微信登录")
    print("=" * 70)

    # 模拟小程序的 wx.login() 获取的 code
    # 注意：这里使用的是测试 code，真实的 code 需要从微信小程序获取
    test_code = "test_code_123"

    print(f"\n1. 发送登录请求 (code: {test_code})...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"code": test_code},
            timeout=10
        )

        print(f"   状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 登录成功！")
            print(f"   Token: {data['access_token'][:30]}...")
            print(f"   用户 ID: {data['user']['id']}")
            print(f"   OpenID: {data['user']['openid'][:20]}...")
            return True
        elif response.status_code == 400:
            error = response.json()
            print(f"   ✗ 登录失败: {error.get('detail', '未知错误')}")
            print(f"\n   提示: 这是因为使用了测试 code，微信 API 会返回错误。")
            print(f"   真实的小程序登录会使用微信生成的有效 code。")
            return False
        else:
            print(f"   ✗ 请求失败: {response.text}")
            return False

    except Exception as e:
        print(f"   ✗ 异常: {e}")
        return False

if __name__ == "__main__":
    print("\n注意：此测试使用模拟 code，微信 API 会返回错误。")
    print("真实的登录需要在微信小程序中调用 wx.login() 获取有效 code。\n")

    test_wechat_login()
