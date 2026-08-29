"""
FastAPI route dependency injection helpers.
"""

from typing import Annotated, Any, Callable, Dict, List, Optional
from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.events import EventBus, get_event_bus
from app.core.idempotency import IdempotencyGuard, get_idempotency_guard
from app.core.security import decode_token, Role, Permission
from app.core.exceptions import AuthenticationError, AuthorizationError

security_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Represents the authenticated principal making a request."""

    def __init__(
        self,
        user_id: str,
        email: str,
        role: str,
        permissions: List[str],
        customer_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.permissions = permissions
        self.customer_id = customer_id
        self.agent_id = agent_id

    def has_permission(self, perm: str) -> bool:
        if self.role in [Role.ADMIN, Role.SUPER_ADMIN]:
            return True
        return perm in self.permissions

    def is_staff(self) -> bool:
        return self.role in Role.STAFF

    def is_customer(self) -> bool:
        return self.role == Role.CUSTOMER


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
) -> Optional[CurrentUser]:
    """Extract authenticated user if bearer token is supplied, else return None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return CurrentUser(
            user_id=payload.get("user_id", payload.get("sub", "")),
            email=payload.get("email", ""),
            role=payload.get("role", Role.CUSTOMER),
            permissions=payload.get("permissions", []),
            customer_id=payload.get("customer_id"),
            agent_id=payload.get("agent_id"),
        )
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
) -> CurrentUser:
    """Enforce a valid bearer JWT and return CurrentUser."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(credentials.credentials)
        return CurrentUser(
            user_id=payload.get("user_id", payload.get("sub", "")),
            email=payload.get("email", ""),
            role=payload.get("role", Role.CUSTOMER),
            permissions=payload.get("permissions", []),
            customer_id=payload.get("customer_id"),
            agent_id=payload.get("agent_id"),
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(allowed_roles: List[str]) -> Callable:
    """Dependency factory enforcing that the authenticated user possesses one of the allowed roles."""

    async def role_checker(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if current_user.role not in allowed_roles and current_user.role != Role.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


def require_permissions(required_permissions: List[str]) -> Callable:
    """Dependency factory enforcing that the user has all listed permissions."""

    async def perm_checker(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if current_user.role in [Role.ADMIN, Role.SUPER_ADMIN]:
            return current_user
        for perm in required_permissions:
            if not current_user.has_permission(perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Missing permission: {perm}",
                )
        return current_user

    return perm_checker


def get_idempotency_key(
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
) -> Optional[str]:
    """Extract optional X-Idempotency-Key header."""
    return x_idempotency_key
