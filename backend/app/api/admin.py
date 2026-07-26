from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password, require_role
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


class UserCreate(BaseModel):
    username: str
    password: str
    employee_id: int
    role: str


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    employee_id: int | None = None
    role: str | None = None
    active: bool | None = None


class UserOut(BaseModel):
    user_id: int
    employee_id: int
    username: str
    role: str
    active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


@router.get("/users", response_model=list[UserOut])
async def list_users(
    _admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).order_by(User.user_id))
    users = result.scalars().all()
    return [
        UserOut(
            user_id=u.user_id,
            employee_id=u.employee_id,
            username=u.username,
            role=u.role,
            active=u.active,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    _admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.execute(
        select(User).where(
            (User.username == body.username) | (User.employee_id == body.employee_id)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or employee_id already exists",
        )

    user = User(
        employee_id=body.employee_id,
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserOut(
        user_id=user.user_id,
        employee_id=user.employee_id,
        username=user.username,
        role=user.role,
        active=user.active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    body: UserUpdate,
    admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.user_id == admin.user_id and body.role is not None and body.role != admin.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change your own role",
        )

    if body.username is not None:
        dup = await session.execute(
            select(User).where(User.username == body.username, User.user_id != user_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
            )
        user.username = body.username

    if body.password is not None:
        user.password_hash = hash_password(body.password)

    if body.employee_id is not None:
        dup = await session.execute(
            select(User).where(User.employee_id == body.employee_id, User.user_id != user_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Employee ID already taken"
            )
        user.employee_id = body.employee_id

    if body.role is not None:
        user.role = body.role

    if body.active is not None:
        if user.user_id == admin.user_id and not body.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deactivate yourself",
            )
        user.active = body.active

    await session.commit()
    await session.refresh(user)
    return UserOut(
        user_id=user.user_id,
        employee_id=user.employee_id,
        username=user.username,
        role=user.role,
        active=user.active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: int,
    admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.user_id == admin.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate yourself",
        )

    user.active = False
    await session.commit()
    return {"detail": f"User {user.username} deactivated"}
