# 用户认证API
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional

from app.core.database import get_db
from app.models.database import User

# 认证路由（/auth/*）
router = APIRouter(prefix="/auth", tags=["认证"])
# 用户资料路由（/user/*）- 与认证共用相同处理函数
user_router = APIRouter(prefix="/user", tags=["用户资料"])

# 密码加密 - 使用 pbkdf2_sha256 替代 bcrypt，没有72字节限制
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT配置
SECRET_KEY = "plant_recognition_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    nickname: str
    avatar_url: Optional[str]
    created_at: str
    last_login_at: Optional[str]


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: UserResponse


class ApiResponse(BaseModel):
    """通用响应"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(user_id: int) -> str:
    """创建访问令牌"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    return user


@router.post("/register", response_model=ApiResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册

    Args:
        request: 注册请求
        db: 数据库会话

    Returns:
        注册结果
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建新用户
    hashed_password = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        password=hashed_password,
        nickname=request.nickname or request.username,
        created_at=datetime.now()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return ApiResponse(
        message="注册成功",
        data={"user_id": new_user.id}
    )


@router.post("/login", response_model=ApiResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录

    Args:
        request: 登录请求
        db: 数据库会话

    Returns:
        登录结果，包含JWT令牌
    """
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 更新最后登录时间
    user.last_login_at = datetime.now()
    db.commit()

    # 创建访问令牌
    token = create_access_token(user.id)

    return ApiResponse(
        message="登录成功",
        data={
            "token": token,
            "user": user.to_dict()
        }
    )


@router.get("/info", response_model=ApiResponse)
async def get_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息

    Args:
        current_user: 当前用户

    Returns:
        用户信息
    """
    return ApiResponse(
        message="获取成功",
        data=current_user.to_dict()
    )


class UpdateProfileRequest(BaseModel):
    """更新资料请求"""
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


@router.post("/profile", response_model=ApiResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料

    Args:
        request: 更新资料请求
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新结果
    """
    if request.nickname is not None:
        current_user.nickname = request.nickname
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url
    if request.bio is not None:
        current_user.bio = request.bio

    db.commit()

    return ApiResponse(
        message="更新成功",
        data=current_user.to_dict()
    )


# ========== 用户资料路由 (/user/*) ==========

@user_router.get("/info", response_model=ApiResponse)
async def user_get_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息 (/user/info)
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户信息
    """
    return ApiResponse(
        message="获取成功",
        data=current_user.to_dict()
    )


@user_router.post("/profile", response_model=ApiResponse)
async def user_update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料 (/user/profile)
    
    Args:
        request: 更新资料请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新结果
    """
    if request.nickname is not None:
        current_user.nickname = request.nickname
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url
    if request.bio is not None:
        current_user.bio = request.bio

    db.commit()

    return ApiResponse(
        message="更新成功",
        data=current_user.to_dict()
    )
