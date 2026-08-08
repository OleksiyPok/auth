# scripts/seed_dev_users.py

import asyncio

from app.auth.rbac.roles import Role
from app.db.session import session_factory
from app.infrastructure.password import hash_password
from app.users.models import User


DEV_USERS = [
    {
        "login": "Manager",
        "password": "Manager",
        "email": "manager@example.com",
        "first_name": "Dev",
        "last_name": "Manager",
        "role": Role.MANAGER,
    },
    {
        "login": "Admin",
        "password": "Admin",
        "email": "admin@example.com",
        "first_name": "Dev",
        "last_name": "Admin",
        "role": Role.ADMIN,
    },
    {
        "login": "User_1",
        "password": "User_1",
        "email": "user_1@example.com",
        "first_name": "Dev",
        "last_name": "User One",
        "role": Role.USER,
    },
    {
        "login": "User_2",
        "password": "User_2",
        "email": "user_2@example.com",
        "first_name": "Dev",
        "last_name": "User Two",
        "role": Role.USER,
    },
]


async def seed_dev_users() -> None:
    async with session_factory() as session:
        for data in DEV_USERS:
            from sqlmodel import select

            result = await session.execute(
                select(User).where(User.login == data["login"])
            )
            user = result.scalar_one_or_none()

            if user:
                print(f"SKIP: {data['login']} already exists ({user.role})")
                continue

            user = User(
                login=data["login"],
                password_hash=hash_password(data["password"]),
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=data["role"],
                is_active=True,
            )
            session.add(user)

        await session.commit()

    print("Development users seeded.")


if __name__ == "__main__":
    asyncio.run(seed_dev_users())