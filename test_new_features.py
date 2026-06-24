"""测试新增功能：笔记、对话、测验反馈"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_notes_api():
    """测试笔记 API"""
    print("=" * 70)
    print("测试笔记 API")
    print("=" * 70)

    # 登录
    print("\n1. 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test_notes"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 登录成功")

    # 创建项目
    print("\n2. 创建项目...")
    project_data = {
        "subject": "测试科目",
        "goal_description": "测试笔记功能",
        "goal_type": "skill"
    }
    project_resp = requests.post(f"{BASE_URL}/api/projects", headers=headers, json=project_data)
    if project_resp.status_code != 201:
        print(f"✗ 创建项目失败: {project_resp.text}")
        return False
    project_id = project_resp.json()["id"]
    print(f"✓ 项目创建成功 (ID: {project_id})")

    # 生成知识图谱
    print("\n3. 生成知识图谱...")
    tree_resp = requests.post(f"{BASE_URL}/api/projects/{project_id}/generate-tree", headers=headers, timeout=300)
    if tree_resp.status_code != 201:
        print(f"✗ 生成知识图谱失败: {tree_resp.text}")
        return False
    print(f"✓ 知识图谱生成成功")

    # 获取节点
    print("\n4. 获取节点...")
    nodes_resp = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree", headers=headers)
    if nodes_resp.status_code != 200:
        print(f"✗ 获取节点失败: {nodes_resp.text}")
        return False
    nodes = nodes_resp.json()["nodes"]
    node_id = nodes[0]["id"]
    print(f"✓ 获取节点成功 (ID: {node_id})")

    # 生成教材
    print("\n5. 生成教材...")
    content_resp = requests.post(f"{BASE_URL}/api/contents/generate", headers=headers, json={"node_id": node_id, "content_type": "lesson"}, timeout=300)
    if content_resp.status_code != 200:
        print(f"✗ 生成教材失败: {content_resp.text}")
        return False
    content_id = content_resp.json()["id"]
    print(f"✓ 教材生成成功 (ID: {content_id})")

    # 添加笔记
    print("\n6. 添加笔记...")
    note_data = {
        "note_type": "note",
        "text": "这是一个测试笔记"
    }
    note_resp = requests.post(f"{BASE_URL}/api/contents/{content_id}/notes", headers=headers, json=note_data)
    if note_resp.status_code != 201:
        print(f"✗ 添加笔记失败: {note_resp.text}")
        return False
    note_id = note_resp.json()["id"]
    print(f"✓ 笔记添加成功 (ID: {note_id})")

    # 获取笔记列表
    print("\n7. 获取笔记列表...")
    notes_resp = requests.get(f"{BASE_URL}/api/contents/{content_id}/notes", headers=headers)
    if notes_resp.status_code != 200:
        print(f"✗ 获取笔记列表失败: {notes_resp.text}")
        return False
    notes = notes_resp.json()["items"]
    print(f"✓ 获取笔记列表成功 ({len(notes)} 条笔记)")

    return True


def test_chat_api():
    """测试对话 API"""
    print("\n" + "=" * 70)
    print("测试对话 API")
    print("=" * 70)

    # 登录（使用同一个用户）
    print("\n1. 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test_notes"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 登录成功")

    # 获取项目
    print("\n2. 获取项目...")
    projects_resp = requests.get(f"{BASE_URL}/api/projects", headers=headers)
    if projects_resp.status_code != 200:
        print(f"✗ 获取项目失败: {projects_resp.text}")
        return False
    projects = projects_resp.json()["items"]
    if not projects:
        print("✗ 没有可用的项目")
        return False
    project_id = projects[0]["id"]
    print(f"✓ 获取项目成功 (ID: {project_id})")

    # 发送对话消息
    print("\n3. 发送对话消息...")
    message = "请简单介绍一下这个科目的核心概念"
    chat_resp = requests.post(f"{BASE_URL}/api/chat/{project_id}", headers=headers, params={"message": message}, timeout=300)
    if chat_resp.status_code != 200:
        print(f"✗ 发送消息失败: {chat_resp.text}")
        return False
    reply = chat_resp.json()["reply"]
    print(f"✓ AI 回复: {reply[:100]}...")

    # 获取对话历史
    print("\n4. 获取对话历史...")
    history_resp = requests.get(f"{BASE_URL}/api/chat/{project_id}/history", headers=headers)
    if history_resp.status_code != 200:
        print(f"✗ 获取历史失败: {history_resp.text}")
        return False
    messages = history_resp.json()["messages"]
    print(f"✓ 获取历史成功 ({len(messages)} 条消息)")

    return True


def test_quiz_feedback():
    """测试测验反馈"""
    print("\n" + "=" * 70)
    print("测试测验反馈")
    print("=" * 70)

    # 登录（使用同一个用户）
    print("\n1. 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "test_notes"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 登录成功")

    # 获取项目
    print("\n2. 获取项目...")
    projects_resp = requests.get(f"{BASE_URL}/api/projects", headers=headers)
    if projects_resp.status_code != 200:
        print(f"✗ 获取项目失败: {projects_resp.text}")
        return False
    projects = projects_resp.json()["items"]
    if not projects:
        print("✗ 没有可用的项目")
        return False
    project_id = projects[0]["id"]
    print(f"✓ 获取项目成功 (ID: {project_id})")

    # 获取节点
    print("\n3. 获取节点...")
    nodes_resp = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree", headers=headers)
    if nodes_resp.status_code != 200:
        print(f"✗ 获取节点失败: {nodes_resp.text}")
        return False
    nodes = nodes_resp.json()["nodes"]
    node_id = nodes[0]["id"]
    print(f"✓ 获取节点成功 (ID: {node_id})")

    # 生成测验
    print("\n4. 生成测验...")
    quiz_resp = requests.post(f"{BASE_URL}/api/quizzes/generate", headers=headers, json={"node_id": node_id, "question_count": 3}, timeout=300)
    if quiz_resp.status_code != 200:
        print(f"✗ 生成测验失败: {quiz_resp.text}")
        return False
    quiz_id = quiz_resp.json()["id"]
    print(f"✓ 测验生成成功 (ID: {quiz_id})")

    # 提交答案
    print("\n5. 提交答案...")
    answers = [
        {"question_index": 0, "answer": "A"},
        {"question_index": 1, "answer": "B"},
        {"question_index": 2, "answer": "C"}
    ]
    submit_resp = requests.post(f"{BASE_URL}/api/quizzes/{quiz_id}/submit", headers=headers, json={"answers": answers})
    if submit_resp.status_code != 200:
        print(f"✗ 提交答案失败: {submit_resp.text}")
        return False
    print(f"✓ 答案提交成功")

    # 提交反馈
    print("\n6. 提交反馈...")
    feedback = {
        "question_0": "confused",
        "question_1": "familiar",
        "question_2": "unclear"
    }
    feedback_resp = requests.post(f"{BASE_URL}/api/quizzes/{quiz_id}/feedback", headers=headers, json=feedback)
    if feedback_resp.status_code != 200:
        print(f"✗ 提交反馈失败: {feedback_resp.text}")
        return False
    print(f"✓ 反馈提交成功")

    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("测试新增功能")
    print("=" * 70)

    results = []

    # 测试笔记 API
    results.append(("笔记 API", test_notes_api()))

    # 测试对话 API
    results.append(("对话 API", test_chat_api()))

    # 测试测验反馈
    results.append(("测验反馈", test_quiz_feedback()))

    # 打印结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败")
    print("=" * 70)
