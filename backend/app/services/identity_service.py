"""
Identity and User Management Service.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, EntityNotFoundError, ValidationError
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
    verify_otp,
    Role,
)
from app.models.identity import User, UserSession, LoginHistory
from app.models.customer import Customer
from app.models.agent import Agent
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
)


class IdentityService:
    @staticmethod
    async def register_user(session: AsyncSession, request: UserRegisterRequest) -> User:
        # Check if email already exists
        existing = await session.scalar(select(User).where(User.email == request.email.lower()))
        if existing:
            raise ConflictError(f"User with email '{request.email}' already exists.")

        user = User(
            email=request.email.lower(),
            hashed_password=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
            role=request.role if request.role in Role.ALL else Role.CUSTOMER,
            is_active=True,
            is_verified=False,
        )
        session.add(user)
        await session.flush()

        # If role is CUSTOMER, automatically create matching Customer profile if needed
        if user.role == Role.CUSTOMER:
            customer = Customer(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone_number,
            )
            session.add(customer)
            await session.flush()

        return user

    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        request: UserLoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        user = await session.scalar(select(User).where(User.email == request.email.lower()))
        
        now = datetime.now(timezone.utc)
        if not user:
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("Account is inactive. Please contact support.")

        if user.locked_until and user.locked_until > now:
            raise AuthenticationError(f"Account locked due to multiple failed login attempts until {user.locked_until.isoformat()}.")

        if not verify_password(request.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = now + timedelta(minutes=15)
            
            # Log failed login
            log = LoginHistory(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                status="FAILED",
                failure_reason="Invalid credentials",
            )
            session.add(log)
            await session.commit()
            raise AuthenticationError("Invalid email or password.")

        # Reset failed attempts on success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now

        # Find customer_id or agent_id if applicable
        customer_id = None
        agent_id = None
        if user.role == Role.CUSTOMER:
            cust = await session.scalar(select(Customer).where(Customer.user_id == user.id))
            if cust:
                customer_id = cust.id
        elif user.role in Role.STAFF:
            ag = await session.scalar(select(Agent).where(Agent.user_id == user.id))
            if ag:
                agent_id = ag.id

        # Generate tokens
        access_token = create_access_token(
            subject=user.id,
            role=user.role,
            email=user.email,
            user_id=user.id,
            customer_id=customer_id,
            agent_id=agent_id,
        )
        refresh_token = create_refresh_token(user_id=user.id)

        # Store session
        user_session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        session.add(user_session)

        # Log success
        log = LoginHistory(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )
        session.add(log)
        await session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            email=user.email,
            role=user.role,
            permissions=decode_token(access_token).get("permissions", []),
            customer_id=customer_id,
            agent_id=agent_id,
        )

    @staticmethod
    async def refresh_access_token(session: AsyncSession, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token type.")

        user_id = payload.get("sub")
        db_session = await session.scalar(
            select(UserSession).where(
                UserSession.refresh_token == refresh_token,
                UserSession.is_revoked == False,
            )
        )
        if not db_session or db_session.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("Refresh token is expired or revoked.")

        user = await session.scalar(select(User).where(User.id == user_id, User.is_active == True))
        if not user:
            raise AuthenticationError("User not found or inactive.")

        customer_id = None
        agent_id = None
        if user.role == Role.CUSTOMER:
            cust = await session.scalar(select(Customer).where(Customer.user_id == user.id))
            if cust:
                customer_id = cust.id
        elif user.role in Role.STAFF:
            ag = await session.scalar(select(Agent).where(Agent.user_id == user.id))
            if ag:
                agent_id = ag.id

        new_access = create_access_token(
            subject=user.id,
            role=user.role,
            email=user.email,
            user_id=user.id,
            customer_id=customer_id,
            agent_id=agent_id,
        )

        return TokenResponse(
            access_token=new_access,
            refresh_token=refresh_token,
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            email=user.email,
            role=user.role,
            permissions=decode_token(new_access).get("permissions", []),
            customer_id=customer_id,
            agent_id=agent_id,
        )

    @staticmethod
    async def request_password_reset(session: AsyncSession, request: PasswordResetRequest) -> str:
        user = await session.scalar(select(User).where(User.email == request.email.lower()))
        if not user:
            # Return dummy success to prevent account enumeration
            return "If the email is registered, an OTP has been sent."

        otp = generate_otp(6)
        user.otp_code = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        await session.commit()
        return otp  # Returned for mock/development notification delivery

    @staticmethod
    async def confirm_password_reset(session: AsyncSession, request: PasswordResetConfirmRequest) -> bool:
        user = await session.scalar(select(User).where(User.email == request.email.lower()))
        if not user or not user.otp_code or not user.otp_expires_at:
            raise ValidationError("Invalid or expired OTP.")

        if not verify_otp(request.otp_code, user.otp_code, user.otp_expires_at):
            raise ValidationError("Invalid or expired OTP.")

        user.hashed_password = hash_password(request.new_password)
        user.otp_code = None
        user.otp_expires_at = None
        user.failed_login_attempts = 0
        user.locked_until = None
        await session.commit()
        return True
