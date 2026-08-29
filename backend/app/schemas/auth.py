"""
Authentication, User registration, Token, and MFA schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema


class UserRegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: Optional[str] = None
    role: str = Field(default="CUSTOMER")


class UserLoginRequest(BaseSchema):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_id: str
    email: str
    role: str
    permissions: List[str]
    customer_id: Optional[str] = None
    agent_id: Optional[str] = None


class UserResponse(BaseSchema):
    id: str
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    is_mfa_enabled: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime


class PasswordResetRequest(BaseSchema):
    email: EmailStr


class PasswordResetConfirmRequest(BaseSchema):
    email: EmailStr
    otp_code: str
    new_password: str = Field(..., min_length=8)


class MFASetupResponse(BaseSchema):
    secret: str
    qr_code_url: str
    recovery_codes: List[str]


class MFAVerifyRequest(BaseSchema):
    otp_code: str
