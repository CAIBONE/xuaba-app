"""用户认证 API"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import httpx

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, LoginResponse, UserResponse, UserUpdate

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
    3. 后端调用微信 code2Session API 换取 openid
    4. 创建/更新用户记录
    5. 返回 JWT token
    """
    # 调用微信 API 换取 openid
    wechat_url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": request.code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(wechat_url, params=params)
        wechat_data = response.json()

    # 检查微信返回的错误
    if "errcode" in wechat_data and wechat_data["errcode"] != 0:
        raise HTTPException(
            status_code=400,
            detail=f"微信登录失败: {wechat_data.get('errmsg', '未知错误')}"
        )

    openid = wechat_data["openid"]

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
async def get_me(
    user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户资料（昵称、头像等）"""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


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
