"""测试项目创建 API"""
import requests
import json
import sys

# 设置 UTF-8 编码
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_project_creation():
    """测试项目创建"""
    print("Step 1: Login to get token...")

    # 登录获取 token
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test123"})
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return False

    token = login_response.json()["access_token"]
    print(f"✓ Login successful, token: {token[:20]}...")

    print("\nStep 2: Create project for 中级经济师...")

    # 创建项目
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    project_data = {
        "subject": "中级经济师",
        "goal_description": "零基础通过2026年中级经济师考试（经济基础+工商管理）",
        "goal_type": "exam",
        "deadline": "2026-11-30"
    }

    create_response = requests.post(f"{BASE_URL}/api/projects", headers=headers, json=project_data)

    if create_response.status_code == 201:
        project = create_response.json()
        print(f"✓ Project created successfully!")
        print(f"  Project ID: {project['id']}")
        print(f"  Subject: {project['subject']}")
        print(f"  Goal: {project['goal_description']}")
        print(f"  Deadline: {project['deadline']}")
        return True
    else:
        print(f"✗ Project creation failed: {create_response.status_code}")
        print(f"  Error: {create_response.text}")
        return False

if __name__ == "__main__":
    print("Testing Project Creation API...\n")
    if test_project_creation():
        print("\n✓ Test passed!")
    else:
        print("\n✗ Test failed!")
