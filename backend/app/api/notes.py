"""笔记 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.content import Content
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteListResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/contents/{content_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    content_id: int,
    data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """创建笔记/划线/提问"""
    # 验证教材存在
    result = await db.execute(select(Content).where(Content.id == content_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="教材不存在")

    note = Note(
        content_id=content_id,
        user_id=user.id,
        note_type=data.note_type,
        text=data.text,
        highlight_range=data.highlight_range,
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return NoteResponse.model_validate(note)


@router.get("/contents/{content_id}/notes", response_model=NoteListResponse)
async def list_notes(
    content_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取教材的笔记列表"""
    query = select(Note).where(
        Note.content_id == content_id,
        Note.user_id == user.id
    ).order_by(Note.created_at.desc())

    result = await db.execute(query)
    notes = result.scalars().all()

    return NoteListResponse(
        total=len(notes),
        items=[NoteResponse.model_validate(n) for n in notes]
    )


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """删除笔记"""
    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == user.id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    await db.delete(note)
