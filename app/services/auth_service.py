from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import UserLoginRequest, UserSignupRequest


async def signup_user(db: AsyncSession, payload: UserSignupRequest) -> User:
    stmt = select(User).where(User.email == payload.email)
    existing_user = (await db.execute(stmt)).scalar_one_or_none()
    if existing_user:
        logger.warning(f"Signup attempt with existing email: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(
        f"User created: {user.id}",
        extra={"extra_data": {"user_id": str(user.id), "email": user.email}}
    )
    return user


async def login_user(db: AsyncSession, payload: UserLoginRequest) -> tuple[User, str]:
    stmt = select(User).where(User.email == payload.email)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email})

    logger.info(
        f"User logged in: {user.id}",
        extra={"extra_data": {"user_id": str(user.id), "email": user.email}}
    )
    return user, token
