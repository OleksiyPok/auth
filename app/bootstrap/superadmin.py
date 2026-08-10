# app/bootstrap/superadmin.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac.roles import Role
from app.core.config import settings
from app.infrastructure.password import hash_password
from app.local_auth.models import LocalIdentity
from app.users.models import User


async def create_initial_superadmin(session: AsyncSession) -> None:
    """Create the initial SUPERADMIN for a brand-new database."""
    superadmin = User(
        email=settings.SUPERADMIN_EMAIL,
        first_name=settings.SUPERADMIN_FIRST_NAME,
        last_name=settings.SUPERADMIN_LAST_NAME,
        role=Role.SUPERADMIN,
        is_active=True,
    )

    session.add(superadmin)

    await session.flush()

    identity = LocalIdentity(
        user_id=superadmin.id,
        login=settings.SUPERADMIN_LOGIN,
        password_hash=hash_password(settings.SUPERADMIN_PASSWORD),
    )

    session.add(identity)
    await session.commit()
