"""知识图谱验证服务 - 6 步验证"""
from typing import Optional


class TreeValidationError(Exception):
    """知识图谱验证错误"""
    pass


def validate_tree(tree: dict) -> tuple[bool, list[str]]:
    """
    6 步验证知识图谱

    Returns:
        (is_valid, errors)
    """
    errors = []

    # Step 1: JSON schema 验证
    if "knowledge_points" not in tree:
        errors.append("缺少 knowledge_points 字段")
        return False, errors

    knowledge_points = tree["knowledge_points"]
    if not isinstance(knowledge_points, list):
        errors.append("knowledge_points 必须是列表")
        return False, errors

    if len(knowledge_points) < 5:
        errors.append(f"知识点太少（{len(knowledge_points)}），至少需要 5 个")

    if len(knowledge_points) > 100:
        errors.append(f"知识点太多（{len(knowledge_points)}），最多 100 个")

    # Step 2: nodeId 唯一性验证
    node_keys = set()
    for kp in knowledge_points:
        if "node_key" not in kp:
            errors.append(f"知识点缺少 node_key: {kp.get('title', '未知')}")
            continue

        if kp["node_key"] in node_keys:
            errors.append(f"node_key 重复: {kp['node_key']}")
        node_keys.add(kp["node_key"])

    # Step 3: prerequisites 引用完整性验证
    for kp in knowledge_points:
        prerequisites = kp.get("prerequisites", [])
        for prereq in prerequisites:
            if prereq not in node_keys:
                errors.append(f"知识点 {kp['node_key']} 的前置 {prereq} 不存在")

    # Step 4: 环检测 (DFS)
    def has_cycle(node_key: str, visited: set, path: set) -> bool:
        if node_key in path:
            return True
        if node_key in visited:
            return False

        visited.add(node_key)
        path.add(node_key)

        kp = next((k for k in knowledge_points if k["node_key"] == node_key), None)
        if kp:
            for prereq in kp.get("prerequisites", []):
                if has_cycle(prereq, visited, path.copy()):
                    return True

        return False

    visited = set()
    for kp in knowledge_points:
        if has_cycle(kp["node_key"], visited, set()):
            errors.append(f"检测到依赖环，涉及 {kp['node_key']}")
            break

    # Step 5: 深度和时间范围验证
    levels = {}
    for kp in knowledge_points:
        level = kp.get("level", 0)
        if level < 0 or level > 5:
            errors.append(f"知识点 {kp['node_key']} 的层级 {level} 不合理（应在 0-5 之间）")

        levels[level] = levels.get(level, 0) + 1

        estimated_minutes = kp.get("estimated_minutes", 30)
        if estimated_minutes < 5 or estimated_minutes > 120:
            errors.append(f"知识点 {kp['node_key']} 的预计时间 {estimated_minutes} 分钟不合理（应在 5-120 之间）")

    # Step 6: 内容合理性验证
    # 6.1 根节点数量（level 0）
    root_count = levels.get(0, 0)
    if root_count < 2:
        errors.append(f"根节点（level 0）太少（{root_count}），至少需要 2 个起点")
    if root_count > 15:
        errors.append(f"根节点（level 0）太多（{root_count}），建议 2-15 个")

    # 6.2 检查每个知识点是否有标题和描述
    for kp in knowledge_points:
        if not kp.get("title", "").strip():
            errors.append(f"知识点 {kp.get('node_key', '未知')} 缺少标题")

        if not kp.get("description", "").strip():
            errors.append(f"知识点 {kp.get('node_key', '未知')} 缺少描述")

    # 6.3 层级分布合理性
    max_level = max(levels.keys()) if levels else 0
    if max_level > 5:
        errors.append(f"层级太深（{max_level}），建议不超过 5 层")

    is_valid = len(errors) == 0
    return is_valid, errors
