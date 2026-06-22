"""测试第二个场景：LLM 学习"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_llm_learning_scenario():
    """测试 LLM 学习场景"""
    print("=" * 70)
    print("测试第二个场景：3个月学会 LLM 及相关基础")
    print("=" * 70)

    # Step 1: 登录
    print("\n[1/6] 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test_llm"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ 登录成功")

    # Step 2: 创建 LLM 学习项目
    print("\n[2/6] 创建 LLM 学习项目...")
    project_data = {
        "subject": "LLM 与 AI 开发",
        "goal_description": "3个月学会 LLM 及相关基础，并可以自主开发 agent 项目",
        "goal_type": "skill",
        "deadline": "2026-09-22"
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

    # Step 4: 获取知识点列表
    print("\n[4/6] 获取知识点列表...")
    nodes_resp = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree", headers=headers)
    if nodes_resp.status_code != 200:
        print(f"✗ 获取知识点列表失败: {nodes_resp.text}")
        return False
    nodes = nodes_resp.json()["nodes"]
    print(f"✓ 获取知识点列表成功")
    print(f"  总知识点: {len(nodes)}")

    # 展示层级分布
    levels = {}
    for node in nodes:
        level = node['level']
        levels[level] = levels.get(level, 0) + 1
    print(f"\n  层级分布:")
    for level in sorted(levels.keys()):
        print(f"    Level {level}: {levels[level]} 个知识点")

    # 展示前 5 个知识点
    print(f"\n  知识点示例（前 5 个）:")
    for i, node in enumerate(nodes[:5], 1):
        print(f"    {i}. [{node['node_key']}] {node['title']}")
        if node.get('description'):
            print(f"       {node['description'][:60]}...")

    # Step 5: 选择第一个知识点生成教材
    first_node = nodes[0]
    node_id = first_node["id"]
    print(f"\n[5/6] 为第一个知识点生成教材...")
    print(f"  知识点: {first_node['title']}")

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
    print(f"  字数: {content['word_count']}")

    # Step 6: 生成测验
    print(f"\n[6/6] 生成测验题目...")
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

    return True

if __name__ == "__main__":
    if test_llm_learning_scenario():
        print("\n" + "=" * 70)
        print("✓ LLM 学习场景测试通过！")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✗ 测试失败！")
        print("=" * 70)
