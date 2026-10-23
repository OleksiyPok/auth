# app/users/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.email_auth.repository.repository import EmailIdentityRepository
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.google_auth.repository.repository import GoogleAuthRepository
from app.google_auth.repository.repository_interface import (
    GoogleAuthRepositoryInterface,
)
from app.merge.repository.repository import MergeProofRepository
from app.merge.repository.repository_interface import MergeProofRepositoryInterface
from app.sessions.dependencies import get_session_repository, get_sessions_service
from app.sessions.repository.repository_interface import SessionRepositoryInterface
from app.sessions.services.service_interface import SessionServiceInterface
from app.two_factor.repository.repository import TwoFactorRepository
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface
from app.username_auth.repository.repository import UsernameIdentityRepository
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)
from app.users.repository.repository import UserRepository
from app.users.repository.repository_interface import UserRepositoryInterface
from app.users.services.service import UserService
from app.users.services.service_interface import UserServiceInterface


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepositoryInterface:
    return UserRepository(session)


# The repositories below are built here, not imported from the dependencies
# of their features: those modules import this one, which would be a cycle.
async def get_user_two_factor_repository(
    session: AsyncSession = Depends(get_session),
) -> TwoFactorRepositoryInterface:
    return TwoFactorRepository(session)


async def get_user_username_identity_repository(
    session: AsyncSession = Depends(get_session),
) -> UsernameIdentityRepositoryInterface:
    return UsernameIdentityRepository(session)


async def get_user_email_identity_repository(
    session: AsyncSession = Depends(get_session),
) -> EmailIdentityRepositoryInterface:
    return EmailIdentityRepository(session)


async def get_user_google_auth_repository(
    session: AsyncSession = Depends(get_session),
) -> GoogleAuthRepositoryInterface:
    return GoogleAuthRepository(session)


async def get_user_merge_proof_repository(
    session: AsyncSession = Depends(get_session),
) -> MergeProofRepositoryInterface:
    return MergeProofRepository(session)


async def get_user_service(
    repository: UserRepositoryInterface = Depends(get_user_repository),
    session_service: SessionServiceInterface = Depends(get_sessions_service),
    session_repository: SessionRepositoryInterface = Depends(get_session_repository),
    two_factor_repository: TwoFactorRepositoryInterface = Depends(
        get_user_two_factor_repository
    ),
    username_identity_repository: UsernameIdentityRepositoryInterface = Depends(
        get_user_username_identity_repository
    ),
    email_identity_repository: EmailIdentityRepositoryInterface = Depends(
        get_user_email_identity_repository
    ),
    google_auth_repository: GoogleAuthRepositoryInterface = Depends(
        get_user_google_auth_repository
    ),
    merge_proof_repository: MergeProofRepositoryInterface = Depends(
        get_user_merge_proof_repository
    ),
) -> UserServiceInterface:
    return UserService(
        repository,
        session_service,
        session_repository,
        two_factor_repository,
        username_identity_repository,
        email_identity_repository,
        google_auth_repository,
        merge_proof_repository,
    )
