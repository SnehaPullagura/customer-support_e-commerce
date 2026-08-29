"""
Unit & API tests for Authentication, User Lifecycle, and RBAC.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, decode_token, Role
from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.services.identity_service import IdentityService


@pytest.mark.asyncio
async def test_password_hashing():
    plain = "SuperSecurePassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_user_registration_and_login(test_session: AsyncSession):
    reg_req = UserRegisterRequest(
        email="test.agent@ecommerce.internal",
        password="ValidPassword123!",
        first_name="Test",
        last_name="Agent",
        role=Role.AGENT,
    )
    user = await IdentityService.register_user(test_session, reg_req)
    assert user.id is not None
    assert user.email == "test.agent@ecommerce.internal"
    assert user.role == Role.AGENT

    # Authenticate
    login_req = UserLoginRequest(
        email="test.agent@ecommerce.internal",
        password="ValidPassword123!",
    )
    token_resp = await IdentityService.authenticate_user(test_session, login_req)
    assert token_resp.access_token is not None
    assert token_resp.refresh_token is not None

    decoded = decode_token(token_resp.access_token)
    assert decoded["email"] == "test.agent@ecommerce.internal"
    assert decoded["role"] == Role.AGENT
    assert "case:read" in decoded["permissions"]


@pytest.mark.asyncio
async def test_auth_api_endpoints(client: AsyncClient):
    # Register via API
    reg_payload = {
        "email": "api.user@example.com",
        "password": "Password123!",
        "first_name": "API",
        "last_name": "User",
        "role": "CUSTOMER",
    }
    res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["email"] == "api.user@example.com"

    # Login via API
    login_payload = {
        "email": "api.user@example.com",
        "password": "Password123!",
    }
    res_login = await client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()["data"]
    token = token_data["access_token"]

    # Access /me
    res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["data"]["email"] == "api.user@example.com"
