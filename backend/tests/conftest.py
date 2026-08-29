"""
Pytest configuration, asynchronous test fixtures, and mock factories.
"""

import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base, get_db
from app.core.security import create_access_token, Role
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh in-memory SQLite database session per test."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client with overridden get_db dependency."""
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def admin_token() -> str:
    return create_access_token(
        subject="admin-123",
        role=Role.ADMIN,
        email="admin@test.internal",
        user_id="admin-123",
    )


@pytest.fixture
def agent_token() -> str:
    return create_access_token(
        subject="agent-456",
        role=Role.AGENT,
        email="agent@test.internal",
        user_id="agent-456",
        agent_id="agent-456",
    )


@pytest.fixture
def customer_token() -> str:
    return create_access_token(
        subject="cust-789",
        role=Role.CUSTOMER,
        email="customer@test.internal",
        user_id="cust-789",
        customer_id="cust-789",
    )
