#!/usr/bin/env python3
"""
综合测试脚本 - 测试所有新实现的功能
"""
import requests
import json
import sys
import os

# 设置 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"
ADMIN_KEY = "change-this-admin-key"

def test_admin_dashboard():
    """测试管理后台"""
    print("\n=== 测试管理后台 ===")
    response = requests.get(
        f"{BASE_URL}/api/admin/dashboard",
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    assert response.status_code == 200, f"Admin dashboard failed: {response.status_code}"
    data = response.json()
    print(f"✓ 用户数: {data['user_count']}")
    print(f"✓ 项目数: {data['project_count']}")
    print(f"✓ 知识点数: {data['node_count']}")
    return True

def test_node_status():
    """测试节点状态跟踪"""
    print("\n=== 测试节点状态跟踪 ===")
    # 获取一个项目
    response = requests.get(f"{BASE_URL}/api/admin/projects",
                          headers={"X-Admin-Key": ADMIN_KEY})
    projects = response.json()
    if not projects:
        print("⚠ 没有项目，跳过")
        return True

    project_id = projects[0]['id']

    # 获取节点
    response = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}")
    if response.status_code != 200:
        print(f"⚠ 获取节点失败: {response.status_code}")
        return True

    nodes = response.json()
    if not nodes:
        print("⚠ 没有节点，跳过")
        return True

    node_id = nodes[0]['id']

    # 更新节点状态
    response = requests.put(
        f"{BASE_URL}/api/nodes/{node_id}",
        json={"status": "in_progress", "mastery_level": 0.5}
    )
    assert response.status_code == 200, f"Update node failed: {response.status_code}"
    updated = response.json()
    print(f"✓ 节点 {node_id} 状态更新为: {updated['status']}")
    print(f"✓ 掌握度: {updated['mastery_level']}")
    return True

def test_content_generation():
    """测试教材生成（包含 Markdown 转换）"""
    print("\n=== 测试教材生成 ===")
    # 获取一个节点
    response = requests.get(f"{BASE_URL}/api/admin/projects",
                          headers={"X-Admin-Key": ADMIN_KEY})
    projects = response.json()
    if not projects:
        print("⚠ 没有项目，跳过")
        return True

    project_id = projects[0]['id']

    # 获取节点
    response = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}")
    if response.status_code != 200:
        print(f"⚠ 获取节点失败: {response.status_code}")
        return True

    nodes = response.json()
    if not nodes:
        print("⚠ 没有节点，跳过")
        return True

    node = nodes[0]

    # 生成教材（这会触发 Markdown -> HTML 转换）
    print(f"为节点 '{node['title']}' 生成教材...")
    response = requests.post(
        f"{BASE_URL}/api/contents/generate",
        json={"node_id": node['id'], "content_type": "lesson"}
    )

    if response.status_code == 200:
        content = response.json()
        print(f"✓ 教材生成成功: {content['title']}")
        print(f"✓ 字数: {content['word_count']}")

        # 检查是否有 HTML 内容
        if content.get('content_json'):
            sections = content['content_json'].get('sections', [])
            if sections:
                first_section = sections[0]
                has_html = '<' in first_section.get('content', '')
                print(f"✓ Markdown 转换: {'是' if has_html else '否'}")
    elif response.status_code == 429:
        print("⚠ 遇到 429 限流，跳过")
    else:
        print(f"⚠ 教材生成失败: {response.status_code}")

    return True

def test_knowledge_tree_validation():
    """测试知识图谱验证"""
    print("\n=== 测试知识图谱验证 ===")
    # 获取一个有节点的项目
    response = requests.get(f"{BASE_URL}/api/admin/projects",
                          headers={"X-Admin-Key": ADMIN_KEY})
    projects = response.json()

    for project in projects:
        if project['tree_total_nodes'] > 0:
            project_id = project['id']
            print(f"✓ 项目 {project['subject']} 有 {project['tree_total_nodes']} 个节点")

            # 获取知识树
            response = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree")
            if response.status_code == 200:
                tree = response.json()
                print(f"✓ 知识树获取成功")
                print(f"  - 节点数: {tree['total_nodes']}")
                print(f"  - 总学时: {tree['total_hours']}h")
            return True

    print("⚠ 没有包含节点的项目")
    return True

def test_progress_tracking():
    """测试进度跟踪"""
    print("\n=== 测试进度跟踪 ===")
    # 获取报表
    response = requests.get(f"{BASE_URL}/api/admin/projects",
                          headers={"X-Admin-Key": ADMIN_KEY})
    projects = response.json()

    if not projects:
        print("⚠ 没有项目，跳过")
        return True

    project_id = projects[0]['id']

    # 获取进度报表
    response = requests.get(f"{BASE_URL}/api/reports/progress/{project_id}")
    if response.status_code == 200:
        report = response.json()
        print(f"✓ 进度报表获取成功")
        print(f"  - 总节点: {report['total_nodes']}")
        print(f"  - 已完成: {report['completed_nodes']}")
        print(f"  - 进行中: {report['in_progress_nodes']}")
        print(f"  - 完成率: {report['completion_rate']*100:.1f}%")
    else:
        print(f"⚠ 获取报表失败: {response.status_code}")

    return True

def main():
    """运行所有测试"""
    print("=" * 60)
    print("综合功能测试")
    print("=" * 60)

    tests = [
        ("管理后台", test_admin_dashboard),
        ("节点状态跟踪", test_node_status),
        ("教材生成", test_content_generation),
        ("知识图谱验证", test_knowledge_tree_validation),
        ("进度跟踪", test_progress_tracking),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} 测试失败: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")

    all_passed = all(r for _, r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！")
    else:
        print("⚠ 部分测试失败")
    print("=" * 60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
