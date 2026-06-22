"""测试完整学习流程"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_complete_learning_flow():
    """测试完整学习流程：知识点图谱 → 教材生成 → 测验生成"""
    print("=" * 70)
    print("测试完整学习流程（中级经济师场景）")
    print("=" * 70)

    # Step 1: 登录
    print("\n[1/6] 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test_flow"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ 登录成功")

    # Step 2: 创建项目
    print("\n[2/6] 创建学习项目...")
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

    # Step 3: 生成知识点图谱
    print("\n[3/6] 生成知识点图谱（调用 LLM，预计 30-60 秒）...")
    tree_resp = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/generate-tree",
        headers=headers,
        timeout=300
    )
    if tree_resp.status_code != 201:
        print(f"✗ 生成知识点图谱失败: {tree_resp.text}")
        return False
    tree_result = tree_resp.json()
    print(f"✓ 知识点图谱生成成功")
    print(f"  知识点数: {tree_result['total_nodes']}")
    print(f"  预计学时: {tree_result['total_hours']} 小时")

    # Step 4: 获取第一个知识点
    print("\n[4/6] 获取知识点列表...")
    nodes_resp = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree", headers=headers)
    if nodes_resp.status_code != 200:
        print(f"✗ 获取知识点列表失败: {nodes_resp.text}")
        return False
    nodes = nodes_resp.json()["nodes"]
    first_node = nodes[0]
    node_id = first_node["id"]
    print(f"✓ 获取知识点列表成功")
    print(f"  选择第一个知识点: {first_node['title']}")
    print(f"  描述: {first_node.get('description', '无')}")

    # Step 5: 生成教材
    print("\n[5/6] 生成教材内容（调用 LLM，预计 30-60 秒）...")
    content_resp = requests.post(
        f"{BASE_URL}/api/contents/generate",
        headers=headers,
        json={"node_id": node_id, "content_type": "lesson", "difficulty": "normal"},
        timeout=300
    )
    if content_resp.status_code != 200:
        print(f"✗ 生成教材失败: {content_resp.text}")
        return False
    content = content_resp.json()
    print(f"✓ 教材生成成功")
    print(f"  教材 ID: {content['id']}")
    print(f"  标题: {content['title']}")
    print(f"  字数: {content['word_count']}")

    # Step 6: 生成测验
    print("\n[6/6] 生成测验题目（调用 LLM，预计 30-60 秒）...")
    quiz_resp = requests.post(
        f"{BASE_URL}/api/quizzes/generate",
        headers=headers,
        json={"node_id": node_id, "quiz_type": "post_test", "question_count": 5},
        timeout=300
    )
    if quiz_resp.status_code != 200:
        print(f"✗ 生成测验失败: {quiz_resp.text}")
        return False
    quiz = quiz_resp.json()
    print(f"✓ 测验生成成功")
    print(f"  测验 ID: {quiz['id']}")
    print(f"  题目数: {quiz['total_questions']}")

    # 展示测验题目示例
    print(f"\n  题目示例（前 2 道）:")
    for i, q in enumerate(quiz['questions'][:2], 1):
        print(f"    {i}. [{q['type']}] {q['content'][:50]}...")
        if q['type'] == 'choice' and 'options' in q:
            for opt in q['options'][:2]:
                print(f"       {opt}")

    return True

if __name__ == "__main__":
    if test_complete_learning_flow():
        print("\n" + "=" * 70)
        print("✓ 完整学习流程测试通过！")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✗ 测试失败！")
        print("=" * 70)
