import pytest
from app.core.idempotency import IdempotencyGuard
from app.core.exceptions import IdempotencyConflictError, ValidationError


def test_idempotency_guard_lifecycle_and_hash_mismatch():
    guard = IdempotencyGuard()
    key = "idem_key_unique_123"
    payload_a = {"amount": 5000, "customer_id": "cust_1"}

    # 1. First execution starts
    is_cached, cached_resp = guard.start_operation(key, payload_a)
    assert is_cached is False
    assert cached_resp is None

    # 2. Concurrent invocation with same key while IN_PROGRESS raises IdempotencyConflictError
    with pytest.raises(IdempotencyConflictError):
        guard.start_operation(key, payload_a)

    # 3. Complete operation
    guard.complete_operation(key, status_code=200, response_body={"refund_id": "ref_999"})

    # 4. Replay with identical payload returns cached result
    is_cached_2, cached_resp_2 = guard.start_operation(key, payload_a)
    assert is_cached_2 is True
    assert cached_resp_2["body"]["refund_id"] == "ref_999"

    # 5. Replay with mutated payload raises ValidationError
    payload_b = {"amount": 99999, "customer_id": "cust_attacker"}
    with pytest.raises(ValidationError):
        guard.start_operation(key, payload_b)
