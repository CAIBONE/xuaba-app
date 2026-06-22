"""学习项目 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.node import Node
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.api.auth import get_current_user
from app.services.tree_generator import generate_knowledge_tree, flatten_tree

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """创建学习项目（建档）"""
    project = Project(
        user_id=user.id,
        subject=data.subject,
        goal_description=data.goal_description,
        goal_type=data.goal_type,
        deadline=data.deadline,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取用户的学习项目列表"""
    query = select(Project).where(Project.user_id == user.id)

    if status_filter:
        query = query.where(Project.status == status_filter)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 获取列表
    query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()

    return ProjectListResponse(
        total=total,
        items=[ProjectResponse.model_validate(p) for p in projects]
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取项目详情"""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """更新项目"""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/generate-tree", status_code=status.HTTP_201_CREATED)
async def generate_tree(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """生成知识图谱（调用 LLM）"""
    # 验证项目存在且属于当前用户
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 如果已有节点，先清除
    await db.execute(delete(Node).where(Node.project_id == project_id))

    # 调用 LLM 生成知识树
    try:
        tree = await generate_knowledge_tree(
            subject=project.subject,
            goal=project.goal_description,
            goal_type=project.goal_type,
            deadline=str(project.deadline) if project.deadline else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识图谱生成失败: {str(e)}")

    # 扁平化并插入数据库
    flat_nodes = flatten_tree(tree)
    key_to_id = {}  # node_key -> db id

    # 插入所有知识点节点
    for node_data in flat_nodes:
        node = Node(
            project_id=project_id,
            node_key=node_data["node_key"],
            title=node_data["title"],
            description=node_data.get("description", ""),
            parent_id=None,  # 知识点图谱没有父子关系
            level=node_data["level"],
            estimated_minutes=node_data["estimated_minutes"],
            prerequisites=node_data["prerequisites"],  # 存储 node_key 列表
        )
        db.add(node)
        await db.flush()
        key_to_id[node_data["node_key"]] = node.id

    # 更新 prerequisites：将 node_key 转换为 node id
    for node_data in flat_nodes:
        if node_data["prerequisites"]:
            # 将 node_key 列表转换为 id 列表
            prereq_ids = [key_to_id[key] for key in node_data["prerequisites"] if key in key_to_id]
            result = await db.execute(
                select(Node).where(Node.id == key_to_id[node_data["node_key"]])
            )
            node = result.scalar_one()
            node.prerequisites = prereq_ids

    await db.flush()

    # 更新项目元信息
    project.tree_version += 1
    project.tree_total_nodes = len(flat_nodes)
    project.tree_total_hours = sum(n["estimated_minutes"] for n in flat_nodes) / 60.0
    await db.flush()

    return {
        "project_id": project_id,
        "tree_version": project.tree_version,
        "total_nodes": len(flat_nodes),
        "total_hours": round(project.tree_total_hours, 1),
        "message": "知识图谱生成成功",
    }


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """删除项目"""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    await db.delete(project)
