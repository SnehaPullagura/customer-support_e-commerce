"""
Core module exports for the E-Commerce Customer Support Platform.
"""

from app.core.config import settings
from app.core.database import Base, get_db, async_session_factory, engine
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
    verify_otp,
)
from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import (
    AppException,
    EntityNotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    CommerceIntegrationError,
    SLABreachError,
    PlaybookExecutionError,
)

__all__ = [
    "settings",
    "Base",
    "get_db",
    "async_session_factory",
    "engine",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "generate_otp",
    "verify_otp",
    "EventBus",
    "Event",
    "EventTopic",
    "get_event_bus",
    "AppException",
    "EntityNotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "CommerceIntegrationError",
    "SLABreachError",
    "PlaybookExecutionError",
]
