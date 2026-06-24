"""针对两个场景测试新功能：笔记、对话、测验反馈"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_scenario_1():
    """场景1：中级经济师考试"""
    print("\n" + "=" * 70)
    print("场景1：中级经济师考试 - 测试新功能")
    print("=" * 70)

    # 登录
    print("\n1. 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "scenario1"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 登录成功")

    # 创建项目
    print("\n2. 创建中级经济师项目...")
    project_data = {
        "subject": "中级经济师",
        "goal_description": "零基础通过2026年中级经济师考试（经济基础+工商管理）",
        "goal_type": "exam",
        "deadline": "2026-11-30"
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
    print("\n4. 获取知识点...")
    nodes_resp = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree", headers=headers)
    if nodes_resp.status_code != 200:
        print(f"✗ 获取节点失败: {nodes_resp.text}")
        return False
    nodes = nodes_resp.json()["nodes"]
    node_id = nodes[0]["id"]
    print(f"✓ 获取知识点成功 (ID: {node_id}, 共 {len(nodes)} 个知识点)")

    # 生成教材
    print("\n5. 生成教材...")
    content_resp = requests.post(f"{BASE_URL}/api/contents/generate", headers=headers, json={"node_id": node_id, "content_type": "lesson"}, timeout=300)
    if content_resp.status_code != 200:
        print(f"✗ 生成教材失败: {content_resp.text}")
        return False
    content_id = content_resp.json()["id"]
    print(f"✓ 教材生成成功 (ID: {content_id})")

    # 测试笔记功能
    print("\n6. 测试笔记功能...")
    note_data = {
        "note_type": "note",
        "text": "中级经济师考试重点：需求法则表明价格与需求量成反比关系"
    }
    note_resp = requests.post(f"{BASE_URL}/api/contents/{content_id}/notes", headers=headers, json=note_data)
    if note_resp.status_code != 201:
        print(f"✗ 添加笔记失败: {note_resp.text}")
        return False
    print(f"✓ 笔记添加成功")

    # 测试对话功能
    print("\n7. 测试对话功能...")
    message = "请解释一下需求法则和供给法则的区别"
    chat_resp = requests.post(f"{BASE_URL}/api/chat/{project_id}", headers=headers, params={"message": message}, timeout=300)
    if chat_resp.status_code != 200:
        print(f"✗ 对话失败: {chat_resp.text}")
        return False
    reply = chat_resp.json()["reply"]
    print(f"✓ AI 回复成功 (回复长度: {len(reply)} 字)")

    # 生成测验
    print("\n8. 生成测验...")
    quiz_resp = requests.post(f"{BASE_URL}/api/quizzes/generate", headers=headers, json={"node_id": node_id, "question_count": 3}, timeout=300)
    if quiz_resp.status_code != 200:
        print(f"✗ 生成测验失败: {quiz_resp.text}")
        return False
    quiz_id = quiz_resp.json()["id"]
    print(f"✓ 测验生成成功 (ID: {quiz_id})")

    # 提交答案
    print("\n9. 提交测验答案...")
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
    print("\n10. 提交测验反馈...")
    feedback = {
        "question_0": "familiar",
        "question_1": "confused",
        "question_2": "familiar"
    }
    feedback_resp = requests.post(f"{BASE_URL}/api/quizzes/{quiz_id}/feedback", headers=headers, json=feedback)
    if feedback_resp.status_code != 200:
        print(f"✗ 提交反馈失败: {feedback_resp.text}")
        return False
    print(f"✓ 反馈提交成功")

    return True


def test_scenario_2():
    """场景2：LLM学习"""
    print("\n" + "=" * 70)
    print("场景2：3个月学会LLM及相关基础 - 测试新功能")
    print("=" * 70)

    # 登录
    print("\n1. 登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"code": "scenario2"})
    if login_resp.status_code != 200:
        print(f"✗ 登录失败: {login_resp.text}")
        return False
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 登录成功")

    # 创建项目
    print("\n2. 创建LLM学习项目...")
    project_data = {
        "subject": "LLM与AI开发",
        "goal_description": "3个月学会LLM及相关基础，并可以自主开发agent项目",
        "goal_type": "skill",
        "deadline": "2026-09-30"
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
    print("\n4. 获取知识点...")
    nodes_resp = requests.get(f"{BASE_URL}/api/nodes/project/{project_id}/tree", headers=headers)
    if nodes_resp.status_code != 200:
        print(f"✗ 获取节点失败: {nodes_resp.text}")
        return False
    nodes = nodes_resp.json()["nodes"]
    node_id = nodes[0]["id"]
    print(f"✓ 获取知识点成功 (ID: {node_id}, 共 {len(nodes)} 个知识点)")

    # 生成教材
    print("\n5. 生成教材...")
    content_resp = requests.post(f"{BASE_URL}/api/contents/generate", headers=headers, json={"node_id": node_id, "content_type": "lesson"}, timeout=300)
    if content_resp.status_code != 200:
        print(f"✗ 生成教材失败: {content_resp.text}")
        return False
    content_id = content_resp.json()["id"]
    print(f"✓ 教材生成成功 (ID: {content_id})")

    # 测试笔记功能
    print("\n6. 测试笔记功能...")
    note_data = {
        "note_type": "note",
        "text": "LLM核心概念：Transformer架构、Attention机制、Tokenization"
    }
    note_resp = requests.post(f"{BASE_URL}/api/contents/{content_id}/notes", headers=headers, json=note_data)
    if note_resp.status_code != 201:
        print(f"✗ 添加笔记失败: {note_resp.text}")
        return False
    print(f"✓ 笔记添加成功")

    # 测试对话功能
    print("\n7. 测试对话功能...")
    message = "请解释一下Transformer架构中的自注意力机制是什么"
    chat_resp = requests.post(f"{BASE_URL}/api/chat/{project_id}", headers=headers, params={"message": message}, timeout=300)
    if chat_resp.status_code != 200:
        print(f"✗ 对话失败: {chat_resp.text}")
        return False
    reply = chat_resp.json()["reply"]
    print(f"✓ AI 回复成功 (回复长度: {len(reply)} 字)")

    # 生成测验
    print("\n8. 生成测验...")
    quiz_resp = requests.post(f"{BASE_URL}/api/quizzes/generate", headers=headers, json={"node_id": node_id, "question_count": 3}, timeout=300)
    if quiz_resp.status_code != 200:
        print(f"✗ 生成测验失败: {quiz_resp.text}")
        return False
    quiz_id = quiz_resp.json()["id"]
    print(f"✓ 测验生成成功 (ID: {quiz_id})")

    # 提交答案
    print("\n9. 提交测验答案...")
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
    print("\n10. 提交测验反馈...")
    feedback = {
        "question_0": "familiar",
        "question_1": "familiar",
        "question_2": "confused"
    }
    feedback_resp = requests.post(f"{BASE_URL}/api/quizzes/{quiz_id}/feedback", headers=headers, json=feedback)
    if feedback_resp.status_code != 200:
        print(f"✗ 提交反馈失败: {feedback_resp.text}")
        return False
    print(f"✓ 反馈提交成功")

    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("两个场景新功能测试")
    print("=" * 70)

    results = []

    # 测试场景1
    results.append(("场景1：中级经济师", test_scenario_1()))

    # 测试场景2
    results.append(("场景2：LLM学习", test_scenario_2()))

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
        print("✓ 两个场景的新功能测试全部通过！")
    else:
        print("✗ 部分场景测试失败")
    print("=" * 70)
