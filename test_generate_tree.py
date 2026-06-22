"""测试知识图谱生成 API"""
import requests
import json
import sys

# 设置 UTF-8 编码
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_generate_tree():
    """测试知识图谱生成"""
    print("=" * 60)
    print("测试知识图谱生成 API")
    print("=" * 60)

    print("\nStep 1: 登录获取 token...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test123"})
    if login_response.status_code != 200:
        print(f"✗ 登录失败: {login_response.text}")
        return False

    token = login_response.json()["access_token"]
    print(f"✓ 登录成功，token: {token[:30]}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\nStep 2: 获取项目详情...")
    project_response = requests.get(f"{BASE_URL}/api/projects/1", headers=headers)
    if project_response.status_code == 200:
        project = project_response.json()
        print(f"✓ 项目: {project['subject']}")
        print(f"  目标: {project['goal_description']}")
        print(f"  截止: {project['deadline']}")
    else:
        print(f"✗ 获取项目失败: {project_response.text}")
        return False

    print("\nStep 3: 调用 LLM 生成知识图谱（可能需要 30-60 秒）...")
    generate_response = requests.post(
        f"{BASE_URL}/api/projects/1/generate-tree",
        headers=headers,
        timeout=300  # 5 分钟超时
    )

    if generate_response.status_code == 201:
        result = generate_response.json()
        print(f"\n✓ 知识图谱生成成功！")
        print(f"  版本: v{result['tree_version']}")
        print(f"  节点数: {result['total_nodes']}")
        print(f"  预计学时: {result['total_hours']} 小时")
        print(f"  消息: {result['message']}")
    else:
        print(f"\n✗ 生成失败 (HTTP {generate_response.status_code})")
        print(f"  错误: {generate_response.text}")
        return False

    print("\nStep 4: 获取知识树详情...")
    tree_response = requests.get(f"{BASE_URL}/api/nodes/project/1/tree", headers=headers)
    if tree_response.status_code == 200:
        tree = tree_response.json()
        print(f"\n✓ 知识树获取成功！")
        print(f"  总节点: {tree['total_nodes']}")
        print(f"  总学时: {tree['total_hours']} 小时")

        # 展示前 5 个节点
        print(f"\n  节点列表（前 5 个）:")
        for i, node in enumerate(tree['nodes'][:5], 1):
            indent = "    " if node['level'] == 0 else "      "
            print(f"{indent}{i}. [{node['node_key']}] {node['title']} ({node['estimated_minutes']}分钟)")
    else:
        print(f"✗ 获取知识树失败: {tree_response.text}")
        return False

    return True

if __name__ == "__main__":
    if test_generate_tree():
        print("\n" + "=" * 60)
        print("✓ 测试通过！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 测试失败！")
        print("=" * 60)
