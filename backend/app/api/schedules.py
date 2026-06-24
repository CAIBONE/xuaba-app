"""学习计划 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.services.plan_generator import generate_daily_plan

router = APIRouter()


@router.get("/daily-plan/{project_id}")
async def get_daily_plan(
    project_id: int,
    daily_minutes: int = 60,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取每日学习计划"""
    try:
        plan = await generate_daily_plan(
            project_id=project_id,
            user_id=user.id,
            db=db,
            daily_study_minutes=daily_minutes
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成计划失败: {str(e)}")
