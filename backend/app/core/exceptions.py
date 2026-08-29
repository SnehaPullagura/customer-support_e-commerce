"""
Custom application exception hierarchy for business logic and HTTP error mapping.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundError(AppException):
    def __init__(self, entity_name: str, identifier: Any, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=404,
            error_code="NOT_FOUND",
            details={"entity": entity_name, "identifier": str(identifier), **(details or {})},
        )


class ValidationError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="UNPROCESSABLE_ENTITY",
            details=details,
        )


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHENTICATED",
            details=details,
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Insufficient permissions to perform this action.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            details=details,
        )


class ConflictError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )


class IdempotencyConflictError(AppException):
    def __init__(self, key: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Concurrent operation in progress for idempotency key: {key}",
            status_code=409,
            error_code="IDEMPOTENCY_IN_PROGRESS",
            details={"idempotency_key": key, **(details or {})},
        )


class SLABreachError(AppException):
    def __init__(self, case_id: str, sla_id: str, breach_type: str):
        super().__init__(
            message=f"SLA '{breach_type}' breached for Case {case_id}.",
            status_code=400,
            error_code="SLA_BREACH",
            details={"case_id": case_id, "sla_id": sla_id, "breach_type": breach_type},
        )


class PlaybookExecutionError(AppException):
    def __init__(self, playbook_id: str, step_name: str, reason: str):
        super().__init__(
            message=f"Playbook execution failed at step '{step_name}': {reason}",
            status_code=400,
            error_code="PLAYBOOK_STEP_FAILED",
            details={"playbook_id": playbook_id, "step_name": step_name, "reason": reason},
        )


class CommerceIntegrationError(AppException):
    def __init__(self, operation: str, target: str, reason: str, status_code: int = 502):
        super().__init__(
            message=f"Commerce integration failed during '{operation}' on '{target}': {reason}",
            status_code=status_code,
            error_code="COMMERCE_ADAPTER_ERROR",
            details={"operation": operation, "target": target, "reason": reason},
        )


class RateLimitExceededError(AppException):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
        )
