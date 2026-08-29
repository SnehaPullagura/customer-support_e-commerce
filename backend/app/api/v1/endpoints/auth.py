"""
Authentication & User endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
)
from app.schemas.common import StandardResponse
from app.services.identity_service import IdentityService

router = APIRouter()


@router.post("/register", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await IdentityService.register_user(db, request)
    return StandardResponse(
        message="User registered successfully",
        data=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=StandardResponse[TokenResponse])
async def login(
    request: UserLoginRequest,
    http_req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = http_req.client.host if http_req.client else None
    ua = http_req.headers.get("User-Agent")
    token_resp = await IdentityService.authenticate_user(db, request, ip_address=ip, user_agent=ua)
    return StandardResponse(message="Authentication successful", data=token_resp)


@router.post("/refresh", response_model=StandardResponse[TokenResponse])
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token_resp = await IdentityService.refresh_access_token(db, request.refresh_token)
    return StandardResponse(message="Token refreshed successfully", data=token_resp)


@router.get("/me", response_model=StandardResponse[dict])
async def get_me(current_user: Annotated[CurrentUser, Depends(get_current_user)]):
    return StandardResponse(
        message="Current user profile",
        data={
            "user_id": current_user.user_id,
            "email": current_user.email,
            "role": current_user.role,
            "permissions": current_user.permissions,
            "customer_id": current_user.customer_id,
            "agent_id": current_user.agent_id,
        },
    )


@router.post("/password-reset/request", response_model=StandardResponse[str])
async def request_password_reset(
    request: PasswordResetRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    otp = await IdentityService.request_password_reset(db, request)
    return StandardResponse(
        message="Password reset OTP issued.",
        data=otp,
    )


@router.post("/password-reset/confirm", response_model=StandardResponse[bool])
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    success = await IdentityService.confirm_password_reset(db, request)
    return StandardResponse(message="Password reset successfully", data=success)
