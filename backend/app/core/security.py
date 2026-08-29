"""
Authentication, cryptographic security, tokens, and authorization helpers.
"""

import bcrypt
import re
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

try:
    from jose import jwt, JWTError
    InvalidTokenError = JWTError
    ExpiredSignatureError = JWTError
except ImportError:
    import jwt
    from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError


# Role definitions
class Role:
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    TEAM_LEAD = "TEAM_LEAD"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

    ALL = [CUSTOMER, AGENT, TEAM_LEAD, MANAGER, ADMIN, SUPER_ADMIN]
    STAFF = [AGENT, TEAM_LEAD, MANAGER, ADMIN, SUPER_ADMIN]
    MANAGEMENT = [TEAM_LEAD, MANAGER, ADMIN, SUPER_ADMIN]
    ADMINISTRATORS = [ADMIN, SUPER_ADMIN]


# Permission definitions
class Permission:
    # Cases
    CASE_READ = "case:read"
    CASE_CREATE = "case:create"
    CASE_UPDATE = "case:update"
    CASE_ASSIGN = "case:assign"
    CASE_ESCALATE = "case:escalate"
    CASE_RESOLVE = "case:resolve"
    CASE_CLOSE = "case:close"
    CASE_MERGE = "case:merge"
    CASE_SPLIT = "case:split"

    # Tickets
    TICKET_READ = "ticket:read"
    TICKET_CREATE = "ticket:create"
    TICKET_UPDATE = "ticket:update"

    # Conversations & Messages
    CONVERSATION_READ = "conversation:read"
    CONVERSATION_WRITE = "conversation:write"
    INTERNAL_NOTE_CREATE = "conversation:internal_note"

    # Playbooks & Resolutions
    PLAYBOOK_EXECUTE = "playbook:execute"
    PLAYBOOK_MANAGE = "playbook:manage"
    REFUND_EXECUTE = "refund:execute"
    REFUND_APPROVE_HIGH_VALUE = "refund:approve_high_value"
    REPLACEMENT_EXECUTE = "replacement:execute"

    # SLA & Routing
    SLA_MANAGE = "sla:manage"
    ROUTING_MANAGE = "routing:manage"

    # Agent & Team
    AGENT_MANAGE = "agent:manage"
    TEAM_MANAGE = "team:manage"

    # Knowledge
    KNOWLEDGE_READ = "knowledge:read"
    KNOWLEDGE_WRITE = "knowledge:write"
    KNOWLEDGE_PUBLISH = "knowledge:publish"

    # Analytics & Audit
    ANALYTICS_VIEW = "analytics:view"
    AUDIT_VIEW = "audit:view"

    # System Admin
    SYSTEM_ADMIN = "system:admin"


# Role-to-Permissions Mapping Matrix
admin_permissions = [
    Permission.CASE_READ,
    Permission.CASE_CREATE,
    Permission.CASE_UPDATE,
    Permission.CASE_ASSIGN,
    Permission.CASE_ESCALATE,
    Permission.CASE_RESOLVE,
    Permission.CASE_CLOSE,
    Permission.CASE_MERGE,
    Permission.CASE_SPLIT,
    Permission.TICKET_READ,
    Permission.TICKET_CREATE,
    Permission.TICKET_UPDATE,
    Permission.CONVERSATION_READ,
    Permission.CONVERSATION_WRITE,
    Permission.INTERNAL_NOTE_CREATE,
    Permission.PLAYBOOK_EXECUTE,
    Permission.PLAYBOOK_MANAGE,
    Permission.REPLACEMENT_EXECUTE,
    Permission.REFUND_EXECUTE,
    Permission.REFUND_APPROVE_HIGH_VALUE,
    Permission.SLA_MANAGE,
    Permission.ROUTING_MANAGE,
    Permission.AGENT_MANAGE,
    Permission.TEAM_MANAGE,
    Permission.KNOWLEDGE_READ,
    Permission.KNOWLEDGE_WRITE,
    Permission.KNOWLEDGE_PUBLISH,
    Permission.ANALYTICS_VIEW,
    Permission.AUDIT_VIEW,
    Permission.SYSTEM_ADMIN,
]

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    Role.CUSTOMER: [
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.CONVERSATION_READ,
        Permission.CONVERSATION_WRITE,
        Permission.KNOWLEDGE_READ,
    ],
    Role.AGENT: [
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.CASE_UPDATE,
        Permission.CASE_ESCALATE,
        Permission.CASE_RESOLVE,
        Permission.TICKET_READ,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE,
        Permission.CONVERSATION_READ,
        Permission.CONVERSATION_WRITE,
        Permission.INTERNAL_NOTE_CREATE,
        Permission.PLAYBOOK_EXECUTE,
        Permission.REPLACEMENT_EXECUTE,
        Permission.REFUND_EXECUTE,
        Permission.KNOWLEDGE_READ,
        Permission.KNOWLEDGE_WRITE,
    ],
    Role.TEAM_LEAD: [
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.CASE_UPDATE,
        Permission.CASE_ASSIGN,
        Permission.CASE_ESCALATE,
        Permission.CASE_RESOLVE,
        Permission.CASE_CLOSE,
        Permission.CASE_MERGE,
        Permission.CASE_SPLIT,
        Permission.TICKET_READ,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE,
        Permission.CONVERSATION_READ,
        Permission.CONVERSATION_WRITE,
        Permission.INTERNAL_NOTE_CREATE,
        Permission.PLAYBOOK_EXECUTE,
        Permission.REPLACEMENT_EXECUTE,
        Permission.REFUND_EXECUTE,
        Permission.REFUND_APPROVE_HIGH_VALUE,
        Permission.KNOWLEDGE_READ,
        Permission.KNOWLEDGE_WRITE,
        Permission.KNOWLEDGE_PUBLISH,
        Permission.AGENT_MANAGE,
        Permission.ANALYTICS_VIEW,
    ],
    Role.MANAGER: [
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.CASE_UPDATE,
        Permission.CASE_ASSIGN,
        Permission.CASE_ESCALATE,
        Permission.CASE_RESOLVE,
        Permission.CASE_CLOSE,
        Permission.CASE_MERGE,
        Permission.CASE_SPLIT,
        Permission.TICKET_READ,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE,
        Permission.CONVERSATION_READ,
        Permission.CONVERSATION_WRITE,
        Permission.INTERNAL_NOTE_CREATE,
        Permission.PLAYBOOK_EXECUTE,
        Permission.PLAYBOOK_MANAGE,
        Permission.REPLACEMENT_EXECUTE,
        Permission.REFUND_EXECUTE,
        Permission.REFUND_APPROVE_HIGH_VALUE,
        Permission.SLA_MANAGE,
        Permission.ROUTING_MANAGE,
        Permission.AGENT_MANAGE,
        Permission.TEAM_MANAGE,
        Permission.KNOWLEDGE_READ,
        Permission.KNOWLEDGE_WRITE,
        Permission.KNOWLEDGE_PUBLISH,
        Permission.ANALYTICS_VIEW,
        Permission.AUDIT_VIEW,
    ],
    Role.ADMIN: admin_permissions,
    Role.SUPER_ADMIN: list(admin_permissions),
}


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    if not hashed_password or not plain_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_jwt_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Encode a standardized JWT with subject and expiration."""
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": settings.PROJECT_NAME,
    }
    if additional_claims:
        payload.update(additional_claims)

    encoded = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded


def create_access_token(
    subject: str,
    role: str,
    email: str,
    user_id: str,
    customer_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Issue a signed JWT access token."""
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    claims = {
        "role": role,
        "email": email,
        "user_id": user_id,
        "customer_id": customer_id,
        "agent_id": agent_id,
        "permissions": ROLE_PERMISSIONS.get(role, []),
    }
    return create_jwt_token(subject=user_id, token_type="access", expires_delta=delta, additional_claims=claims)


def create_refresh_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Issue a signed JWT refresh token."""
    delta = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_jwt_token(subject=user_id, token_type="refresh", expires_delta=delta)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except (InvalidTokenError, Exception) as err:
        raise AuthenticationError(f"Invalid authentication token: {str(err)}")


def generate_otp(length: int = 6) -> str:
    """Generate a cryptographically secure numeric OTP."""
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))


def verify_otp(provided_otp: str, stored_otp: str, expires_at: datetime) -> bool:
    """Validate OTP match and expiry."""
    if not provided_otp or not stored_otp:
        return False
    if datetime.now(timezone.utc) > expires_at:
        return False
    return secrets.compare_digest(provided_otp.strip(), stored_otp.strip())


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive information such as credit card numbers, email prefixes,
    and phone numbers in audit logs or public views.
    """
    if not text:
        return ""

    # Credit card / 13-19 digits regex
    masked = re.sub(r"\b(?:\d[ -]*?){13,19}\b", lambda m: "****-****-****-" + m.group(0).replace(" ", "").replace("-", "")[-4:], text)

    # Email masking: j***@example.com
    masked = re.sub(
        r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b",
        r"\1***@\2",
        masked,
    )

    # Phone masking: +123***7890
    masked = re.sub(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", r"***-***-****", masked)

    return masked
