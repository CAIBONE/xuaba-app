"""用户认证 API"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, LoginResponse, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def create_access_token(user_id: int) -> str:
    """创建 JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_exception

    # 从 Authorization header 中提取 token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise credentials_exception

    token = parts[1]

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    微信登录

    流程：
    1. 小程序调用 wx.login() 获取 code
    2. 将 code 发送到后端
    3. 后端用 code 换取 openid
    4. 创建/更新用户记录
    5. 返回 JWT token
    """
    # TODO: 调用微信 API 用 code 换取 openid
    # 目前模拟实现
    openid = f"mock_openid_{request.code}"

    # 查找或创建用户
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if user is None:
        # 创建新用户
        user = User(openid=openid, nickname="新用户")
        db.add(user)
        await db.flush()

    # 创建 token
    access_token = create_access_token(user.id)

    return LoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me")
async def get_me():
    """获取当前用户信息（临时测试版本）"""
    return {
        "id": 999,
        "openid": "test",
        "nickname": "Test User",
        "avatar": "",
        "profile_json": {},
        "created_at": "2026-06-21T00:00:00",
        "updated_at": "2026-06-21T00:00:00"
    }


@router.post("/test-login", response_model=LoginResponse)
async def test_login(db: AsyncSession = Depends(get_db)):
    """
    测试登录（仅开发环境）

    创建一个测试用户并返回 token
    """
    # 查找或创建测试用户
    test_openid = "test_user_openid"
    result = await db.execute(select(User).where(User.openid == test_openid))
    user = result.scalar_one_or_none()

    if user is None:
        # 创建测试用户
        user = User(openid=test_openid, nickname="测试用户")
        db.add(user)
        await db.flush()

    # 创建 token
    access_token = create_access_token(user.id)

    return LoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )
