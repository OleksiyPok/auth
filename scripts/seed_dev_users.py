# scripts/seed_dev_users.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio

from sqlmodel import select

from app.auth.rbac.roles import Role
from app.core.identifiers import normalize_email, normalize_username
from app.db.session import session_factory
from app.email_auth.models import EmailIdentity
from app.google_auth.models import GoogleIdentity
from app.infrastructure.password import hash_password
from app.username_auth.models import UsernameIdentity
from app.users.models import User

DEV_USERS = [
    {
        "type": "username",
        "username": "Username_user",
        "password": "Username_user",
        "first_name": "Username_user",
        "last_name": "Develop",
    },
    {
        "type": "email",
        "email": "email_user@example.com",
        "password": "Email_user",
        "first_name": "Email_user",
        "last_name": "Develop",
    },
    {
        "type": "google",
        "google_user_id": "Google-user",
        "first_name": "Google-user",
        "last_name": "Develop",
    },
]


async def seed_dev_users() -> None:
    added_users = []

    async with session_factory() as session:
        async with session.begin():

            # ---------------------------------------------------------
            # Username Identity
            # ---------------------------------------------------------

            username_data = next(
                data for data in DEV_USERS if data["type"] == "username"
            )

            username = normalize_username(username_data["username"])

            result = await session.execute(
                select(UsernameIdentity).where(UsernameIdentity.username == username)
            )

            username_identity = result.scalar_one_or_none()

            if username_identity is None:
                user = User(
                    first_name=username_data["first_name"],
                    last_name=username_data["last_name"],
                    role=Role.USER,
                )

                session.add(user)
                await session.flush()

                identity = UsernameIdentity(
                    user_id=user.id,
                    username=username,
                    password_hash=hash_password(username_data["password"]),
                )

                session.add(identity)
                await session.flush()

                added_users.append(
                    {
                        "type": "Username",
                        "login": username,
                        "password": username_data["password"],
                        "user_id": user.id,
                    }
                )

            # ---------------------------------------------------------
            # Email Identity
            # ---------------------------------------------------------

            email_data = next(data for data in DEV_USERS if data["type"] == "email")
            email = normalize_email(email_data["email"])

            result = await session.execute(
                select(EmailIdentity).where(EmailIdentity.email == email)
            )

            email_identity = result.scalar_one_or_none()

            if email_identity is None:
                user = User(
                    first_name=email_data["first_name"],
                    last_name=email_data["last_name"],
                    role=Role.USER,
                )

                session.add(user)
                await session.flush()

                identity = EmailIdentity(
                    user_id=user.id,
                    email=email,
                    password_hash=hash_password(email_data["password"]),
                )

                session.add(identity)
                await session.flush()

                added_users.append(
                    {
                        "type": "Email",
                        "login": email_data["email"],
                        "password": email_data["password"],
                        "user_id": user.id,
                    }
                )

            # ---------------------------------------------------------
            # Google Identity
            # ---------------------------------------------------------

            google_data = next(data for data in DEV_USERS if data["type"] == "google")

            result = await session.execute(
                select(GoogleIdentity).where(
                    GoogleIdentity.google_user_id == google_data["google_user_id"]
                )
            )
            google_identity = result.scalar_one_or_none()

            if google_identity is None:
                user = User(
                    first_name=google_data["first_name"],
                    last_name=google_data["last_name"],
                    role=Role.USER,
                )

                session.add(user)
                await session.flush()

                identity = GoogleIdentity(
                    user_id=user.id,
                    google_user_id=google_data["google_user_id"],
                )

                session.add(identity)
                await session.flush()

                added_users.append(
                    {
                        "type": "Google",
                        "login": google_data["google_user_id"],
                        "password": None,
                        "user_id": user.id,
                    }
                )

    print("\nDevelopment users seeded.")

    if added_users:
        print("\nAdded users:")
        print("-" * 80)

        for user in added_users:
            print(
                f"Identity: {user['type']:<10} "
                f"Login: {user['login']:<30} "
                f"Role: {Role.USER}"
            )

            if user["password"] is not None:
                print(f"Password: {user['password']:<30}")

            print(f"User ID: {user['user_id']}")
            print()

        print("-" * 80)
        print(f"Total added: {len(added_users)}")
    else:
        print("\nNo new users were added.")


if __name__ == "__main__":
    asyncio.run(seed_dev_users())
