from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_user,
    verify_password,
)
from app.config import settings
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class UserResponse(BaseModel):
    user_id: int
    employee_id: int
    username: str
    role: str
    active: bool


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        role=user.role,
        username=user.username,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(user: User = Depends(get_current_user)):
    token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        role=user.role,
        username=user.username,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        user_id=user.user_id,
        employee_id=user.employee_id,
        username=user.username,
        role=user.role,
        active=user.active,
    )
