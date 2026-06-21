"""知识节点 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse, NodeListResponse, KnowledgeTreeResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    data: NodeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """创建知识节点"""
    # 验证项目存在且属于当前用户
    result = await db.execute(
        select(Project).where(Project.id == data.project_id, Project.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="项目不存在")

    node = Node(
        project_id=data.project_id,
        node_key=data.node_key,
        title=data.title,
        parent_id=data.parent_id,
        level=data.level,
        estimated_minutes=data.estimated_minutes,
        prerequisites=data.prerequisites,
    )
    db.add(node)
    await db.flush()
    await db.refresh(node)
    return NodeResponse.model_validate(node)


@router.get("/project/{project_id}", response_model=NodeListResponse)
async def list_nodes_by_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取项目下的所有节点"""
    # 验证项目存在且属于当前用户
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="项目不存在")

    # 获取节点列表
    query = select(Node).where(Node.project_id == project_id).order_by(Node.level, Node.node_key)
    result = await db.execute(query)
    nodes = result.scalars().all()

    return NodeListResponse(
        total=len(nodes),
        items=[NodeResponse.model_validate(n) for n in nodes]
    )


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取节点详情"""
    result = await db.execute(select(Node).where(Node.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 验证项目属于当前用户
    proj_result = await db.execute(
        select(Project).where(Project.id == node.project_id, Project.user_id == user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    return NodeResponse.model_validate(node)


@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: int,
    data: NodeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """更新节点"""
    result = await db.execute(select(Node).where(Node.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(node, key, value)

    await db.flush()
    await db.refresh(node)
    return NodeResponse.model_validate(node)


@router.get("/project/{project_id}/tree", response_model=KnowledgeTreeResponse)
async def get_knowledge_tree(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取项目知识图谱"""
    # 验证项目存在且属于当前用户
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 获取所有节点
    query = select(Node).where(Node.project_id == project_id).order_by(Node.level, Node.node_key)
    result = await db.execute(query)
    nodes = result.scalars().all()

    # 计算总学时
    total_hours = sum(n.estimated_minutes for n in nodes) / 60.0

    return KnowledgeTreeResponse(
        project_id=project_id,
        nodes=[NodeResponse.model_validate(n) for n in nodes],
        total_nodes=len(nodes),
        total_hours=round(total_hours, 1)
    )
