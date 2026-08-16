# tests/conftest.py

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.db.session import get_session
from app.infrastructure.password import hash_password
from app.username_auth.models import UsernameIdentity
from app.main import app
from app.users.models import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_test_database() -> None:
    async with test_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def drop_test_database() -> None:
    async with test_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    asyncio.run(drop_test_database())
    asyncio.run(create_test_database())

    yield

    asyncio.run(drop_test_database())


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


async def create_user(
    login: str,
    email: str,
    role: str,
) -> User:
    async with test_session_factory() as session:
        user = User(
            email=email,
            first_name=role.capitalize(),
            last_name="User",
            role=role,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        local_identity = UsernameIdentity(
            user_id=user.id,
            login=login,
            password_hash=hash_password("password123"),
        )

        session.add(local_identity)
        await session.commit()

        return user


@pytest.fixture
def regular_user_token(client: TestClient) -> str:
    asyncio.run(
        create_user(
            login="regular_fixture_user",
            email="regular_fixture@example.com",
            role="user",
        )
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "regular_fixture_user",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def admin_user_token(client: TestClient) -> str:
    asyncio.run(
        create_user(
            login="admin_fixture_user",
            email="admin_fixture@example.com",
            role="admin",
        )
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin_fixture_user",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def superadmin_user_token(client: TestClient) -> str:
    asyncio.run(
        create_user(
            login="superadmin_fixture_user",
            email="superadmin_fixture@example.com",
            role="superadmin",
        )
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "superadmin_fixture_user",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]
