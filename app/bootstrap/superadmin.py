# app/bootstrap/superadmin.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac.roles import Role
from app.core.config import settings
from app.email_auth.models import EmailIdentity
from app.infrastructure.password import hash_password
from app.username_auth.models import UsernameIdentity
from app.users.models import User


async def create_initial_superadmin(session: AsyncSession) -> None:
    """Create the initial SUPERADMIN for a brand-new database."""
    superadmin = User(
        first_name=settings.SUPERADMIN_FIRST_NAME,
        last_name=settings.SUPERADMIN_LAST_NAME,
        role=Role.SUPERADMIN,
        is_active=True,
    )

    session.add(superadmin)

    await session.flush()

    username_identity = UsernameIdentity(
        user_id=superadmin.id,
        username=settings.SUPERADMIN_LOGIN,
        password_hash=hash_password(settings.SUPERADMIN_PASSWORD),
    )

    email_identity = EmailIdentity(
        user_id=superadmin.id,
        email=settings.SUPERADMIN_EMAIL.strip().casefold(),
        password_hash=hash_password(settings.SUPERADMIN_PASSWORD),
    )

    session.add(username_identity)
    session.add(email_identity)

    await session.commit()
