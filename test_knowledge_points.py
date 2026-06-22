"""测试知识点图谱生成"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_knowledge_point_graph():
    """测试知识点级别的知识图谱生成"""
    print("=" * 70)
    print("测试知识点图谱生成（中级经济师场景）")
    print("=" * 70)

    print("\nStep 1: 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test_kp"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ 登录成功")

    print("\nStep 2: 创建学习项目...")
    project_data = {
        "subject": "中级经济师",
        "goal_description": "零基础通过2026年中级经济师考试（经济基础+工商管理）",
        "goal_type": "exam",
        "deadline": "2026-11-30"
    }
    create_resp = requests.post(f"{BASE_URL}/api/projects", headers=headers, json=project_data)
    if create_resp.status_code != 201:
        print(f"✗ 创建项目失败: {create_resp.text}")
        return False
    project = create_resp.json()
    project_id = project["id"]
    print(f"✓ 项目创建成功 (ID: {project_id})")
    print(f"  科目: {project['subject']}")
    print(f"  目标: {project['goal_description']}")

    print("\nStep 3: 生成知识点图谱（调用 LLM，预计 30-60 秒）...")
    generate_resp = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/generate-tree",
        headers=headers,
        timeout=300
    )

    if generate_resp.status_code != 201:
        print(f"\n✗ 生成失败 (HTTP {generate_resp.status_code})")
        print(f"  错误: {generate_resp.text}")
        return False

    result = generate_resp.json()
    print(f"\n✓ 知识点图谱生成成功！")
    print(f"  版本: v{result['tree_version']}")
    print(f"  知识点数: {result['total_nodes']}")
    print(f"  预计学时: {result['total_hours']} 小时")

    print("\nStep 4: 获取知识点列表...")
    tree_resp = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree", headers=headers)
    if tree_resp.status_code != 200:
        print(f"✗ 获取失败: {tree_resp.text}")
        return False

    tree = tree_resp.json()
    print(f"\n✓ 知识点列表获取成功！")
    print(f"  总知识点: {tree['total_nodes']}")
    print(f"  总学时: {tree['total_hours']} 小时")

    # 展示知识点结构
    print(f"\n  知识点示例（前 8 个）:")
    for i, node in enumerate(tree['nodes'][:8], 1):
        indent = "  " * node['level']
        prereq = f" (前置: {node['prerequisites']})" if node['prerequisites'] else ""
        print(f"{indent}{i}. [{node['node_key']}] {node['title']}")
        if node.get('description'):
            print(f"{indent}   {node['description']}")
        print(f"{indent}   Level {node['level']}, {node['estimated_minutes']}分钟{prereq}")

    # 统计层级分布
    levels = {}
    for node in tree['nodes']:
        level = node['level']
        levels[level] = levels.get(level, 0) + 1

    print(f"\n  层级分布:")
    for level in sorted(levels.keys()):
        print(f"    Level {level}: {levels[level]} 个知识点")

    return True

if __name__ == "__main__":
    if test_knowledge_point_graph():
        print("\n" + "=" * 70)
        print("✓ 测试通过！")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✗ 测试失败！")
        print("=" * 70)
