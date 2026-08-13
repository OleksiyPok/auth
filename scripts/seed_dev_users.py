# scripts/seed_dev_users.py

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import select

from app.auth.rbac.roles import Role
from app.db.session import session_factory
from app.infrastructure.password import hash_password
from app.local_auth.models import LocalIdentity
from app.users.models import User


DEV_USERS = [
    {
        "login": "Superadmin",
        "password": "Superadmin",
        "email": "superadmin@example.com",
        "first_name": "Dev",
        "last_name": "Superadmin",
        "role": Role.SUPERADMIN,
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
        "login": "Manager",
        "password": "Manager",
        "email": "manager@example.com",
        "first_name": "Dev",
        "last_name": "Manager",
        "role": Role.MANAGER,
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
    added_users = []

    async with session_factory() as session:
        for data in DEV_USERS:
            # Login belongs to LocalIdentity, not User.
            identity_result = await session.execute(
                select(LocalIdentity).where(
                    LocalIdentity.login == data["login"]
                )
            )
            identity = identity_result.scalar_one_or_none()

            if identity:
                print(
                    f"SKIP: {data['login']} already exists "
                    f"(user_id={identity.user_id})"
                )
                continue

            # Create the domain user first.
            user = User(
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=data["role"],
                is_active=True,
            )

            session.add(user)

            # User.id is needed by LocalIdentity.
            await session.flush()

            # Create the local authentication identity.
            identity = LocalIdentity(
                user_id=user.id,
                login=data["login"],
                password_hash=hash_password(data["password"]),
            )

            session.add(identity)

            added_users.append(data)

        await session.commit()

    print("\nDevelopment users seeded.")

    if added_users:
        print("\nAdded users:")
        print("-" * 80)

        for user in added_users:
            print(
                f"Login: {user['login']:<12} "
                f"Password: {user['password']:<12} "
                f"Role: {user['role']:<12} "
                f"Email: {user['email']}"
            )

        print("-" * 80)
        print(f"Total added: {len(added_users)}")
    else:
        print("\nNo new users were added.")


if __name__ == "__main__":
    asyncio.run(seed_dev_users())