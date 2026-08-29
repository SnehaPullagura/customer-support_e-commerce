"""
Distributed idempotency management for safe, repeatable mutations.
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.core.exceptions import IdempotencyConflictError


class IdempotencyRecord:
    def __init__(self, key: str, request_hash: str, status: str = "IN_PROGRESS"):
        self.key = key
        self.request_hash = request_hash
        self.status = status  # 'IN_PROGRESS', 'COMPLETED', 'FAILED'
        self.response_status_code: Optional[int] = None
        self.response_body: Optional[Any] = None
        self.created_at = time.time()
        self.expires_at = self.created_at + settings.IDEMPOTENCY_EXPIRY_SECONDS

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class IdempotencyGuard:
    """
    In-memory and Redis-compatible store to enforce idempotency on sensitive operations
    (e.g., Refund creation, Replacement orders, Notifications, Playbook actions).
    """

    def __init__(self) -> None:
        self._store: Dict[str, IdempotencyRecord] = {}

    def compute_hash(self, payload: Any) -> str:
        """Compute SHA256 fingerprint of request payload."""
        if payload is None:
            return "empty_payload"
        if isinstance(payload, (dict, list)):
            encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        elif isinstance(payload, str):
            encoded = payload.encode("utf-8")
        elif isinstance(payload, bytes):
            encoded = payload
        else:
            encoded = str(payload).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def start_operation(self, key: str, payload: Any) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Attempt to claim an idempotency key.
        Returns:
            (is_cached, cached_response_if_completed)
        Raises:
            IdempotencyConflictError if key is currently IN_PROGRESS.
        """
        self._clean_expired()
        request_hash = self.compute_hash(payload)

        record = self._store.get(key)
        if record:
            if record.status == "IN_PROGRESS":
                raise IdempotencyConflictError(key)
            elif record.status == "COMPLETED":
                # Check for payload mutation / mismatch
                if record.request_hash != request_hash:
                    from app.core.exceptions import ValidationError
                    raise ValidationError(
                        f"Idempotency key '{key}' was previously executed with a different request payload."
                    )
                # Return cached response
                return True, {
                    "status_code": record.response_status_code or 200,
                    "body": record.response_body,
                }

        # Claim the key
        self._store[key] = IdempotencyRecord(key=key, request_hash=request_hash, status="IN_PROGRESS")
        return False, None

    def complete_operation(self, key: str, status_code: int, response_body: Any) -> None:
        """Mark the operation as completed and store the response for replays."""
        record = self._store.get(key)
        if record:
            record.status = "COMPLETED"
            record.response_status_code = status_code
            record.response_body = response_body

    def fail_operation(self, key: str) -> None:
        """Remove or mark the key as failed so retry is permitted."""
        if key in self._store:
            del self._store[key]

    def _clean_expired(self) -> None:
        now = time.time()
        expired_keys = [k for k, v in self._store.items() if now > v.expires_at]
        for k in expired_keys:
            del self._store[k]


_global_idempotency_guard = IdempotencyGuard()


def get_idempotency_guard() -> IdempotencyGuard:
    return _global_idempotency_guard
