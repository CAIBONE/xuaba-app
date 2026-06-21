"""用户认证 API"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, LoginResponse, UserResponse

router = APIRouter()


def create_access_token(user_id: int) -> str:
    """创建 JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    token: str = Depends(lambda: None),  # 后续实现从 header 获取
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # TODO: 从 Authorization header 获取 token
    if not token:
        raise credentials_exception

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


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.model_validate(user)
