"""教材 API"""
from datetime import datetime
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.node import Node
from app.models.content import Content
from app.models.push_record import PushRecord
from app.schemas.content import ContentCreate, ContentResponse, ContentListResponse, GenerateContentRequest, PushContentRequest
from app.api.auth import get_current_user
from app.services.content_generator import generate_content as generate_content_service

router = APIRouter()


@router.post("", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    data: ContentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """创建教材"""
    # 验证节点存在
    result = await db.execute(select(Node).where(Node.id == data.node_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="节点不存在")

    content = Content(
        node_id=data.node_id,
        user_id=data.user_id,
        content_type=data.content_type,
        title=data.title,
        content_json=data.content_json,
        word_count=data.word_count,
        difficulty_level=data.difficulty_level,
    )
    db.add(content)
    await db.flush()
    await db.refresh(content)
    return ContentResponse.model_validate(content)


@router.get("/node/{node_id}", response_model=ContentListResponse)
async def list_contents_by_node(
    node_id: int,
    content_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取节点下的所有教材"""
    query = select(Content).where(Content.node_id == node_id, Content.user_id == user.id)

    if content_type:
        query = query.where(Content.content_type == content_type)

    query = query.order_by(Content.generated_at.desc())
    result = await db.execute(query)
    contents = result.scalars().all()

    return ContentListResponse(
        total=len(contents),
        items=[ContentResponse.model_validate(c) for c in contents]
    )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取教材详情"""
    result = await db.execute(
        select(Content).where(Content.id == content_id, Content.user_id == user.id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="教材不存在")
    return ContentResponse.model_validate(content)


@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    data: GenerateContentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    生成教材（调用 LLM）
    """
    # 验证节点存在
    result = await db.execute(select(Node).where(Node.id == data.node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 调用 LLM 生成教材
    try:
        content_data = await generate_content_service(
            node_title=node.title,
            node_description=node.description,
            content_type=data.content_type,
            prerequisites=None,  # TODO: 查询前置节点标题
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"教材生成失败: {str(e)}")

    # 计算字数
    word_count = 0
    if "sections" in content_data:
        for section in content_data["sections"]:
            word_count += len(section.get("content", ""))
    elif "exercises" in content_data:
        for exercise in content_data["exercises"]:
            word_count += len(exercise.get("question", ""))
            word_count += len(exercise.get("answer", ""))

    # 保存教材
    content = Content(
        node_id=data.node_id,
        user_id=user.id,
        content_type=data.content_type,
        title=content_data.get("title", f"{node.title} - {data.content_type}"),
        content_json=content_data,
        word_count=word_count,
        difficulty_level=data.difficulty,
        audit_status="passed",  # TODO: 实际审计
    )
    db.add(content)
    await db.flush()
    await db.refresh(content)
    return ContentResponse.model_validate(content)


@router.post("/{content_id}/push", response_model=dict)
async def push_content(
    content_id: int,
    data: PushContentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """推送教材给用户"""
    # 获取教材
    result = await db.execute(
        select(Content).where(Content.id == content_id, Content.user_id == user.id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="教材不存在")

    # 创建推送记录
    push_record = PushRecord(
        user_id=user.id,
        content_id=content_id,
        channel=data.channel,
        status="sent",
        pushed_at=datetime.utcnow(),
    )
    db.add(push_record)

    # 更新教材发布时间
    content.published_at = datetime.utcnow()

    await db.flush()

    return {"message": "推送成功", "push_id": push_record.id}


class BatchGenerateRequest(BaseModel):
    node_ids: List[int]
    content_type: str = "lesson"
    difficulty: str = "medium"


@router.post("/batch-generate")
async def batch_generate_content(
    data: BatchGenerateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    批量生成教材（为多个节点生成教材）
    注意：这是同步调用，可能需要较长时间
    """
    results = []
    errors = []

    for node_id in data.node_ids:
        # 验证节点存在
        result = await db.execute(select(Node).where(Node.id == node_id))
        node = result.scalar_one_or_none()
        if not node:
            errors.append({"node_id": node_id, "error": "节点不存在"})
            continue

        # 检查是否已有教材
        existing = await db.execute(
            select(Content).where(
                Content.node_id == node_id,
                Content.user_id == user.id,
                Content.content_type == data.content_type
            )
        )
        if existing.scalar_one_or_none():
            results.append({"node_id": node_id, "status": "already_exists"})
            continue

        # 调用 LLM 生成教材
        try:
            content_data = await generate_content_service(
                node_title=node.title,
                node_description=node.description,
                content_type=data.content_type,
                prerequisites=None,
            )

            # 计算字数
            word_count = 0
            if "sections" in content_data:
                for section in content_data["sections"]:
                    word_count += len(section.get("content", ""))
            elif "exercises" in content_data:
                for exercise in content_data["exercises"]:
                    word_count += len(exercise.get("question", ""))
                    word_count += len(exercise.get("answer", ""))

            # 保存教材
            content = Content(
                node_id=node_id,
                user_id=user.id,
                content_type=data.content_type,
                title=content_data.get("title", f"{node.title} - {data.content_type}"),
                content_json=content_data,
                word_count=word_count,
                difficulty_level=data.difficulty,
                audit_status="passed",
            )
            db.add(content)
            await db.flush()
            results.append({"node_id": node_id, "status": "generated", "content_id": content.id})

        except Exception as e:
            errors.append({"node_id": node_id, "error": str(e)})

    return {
        "total": len(data.node_ids),
        "generated": len([r for r in results if r.get("status") == "generated"]),
        "already_exists": len([r for r in results if r.get("status") == "already_exists"]),
        "errors": len(errors),
        "results": results,
        "error_details": errors
    }
