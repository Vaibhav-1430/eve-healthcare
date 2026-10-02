from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.middleware.rate_limit import RateLimiter
from app.schemas.auth import TokenResponse, UserLoginRequest, UserResponse, UserSignupRequest
from app.services.auth_service import login_user, signup_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_AUTH_PER_MINUTE, key_prefix="rl:auth")


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    dependencies=[Depends(auth_limiter)],
)
async def signup(
    payload: UserSignupRequest,
    db: AsyncSession = Depends(get_db),
):
    return await signup_user(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain JWT token",
    dependencies=[Depends(auth_limiter)],
)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user, token = await login_user(db, payload)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
