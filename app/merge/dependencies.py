# app/merge/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.email_auth.repository.repository import EmailIdentityRepository
from app.identities.dependencies import get_identity_service
from app.identities.services.service_interface import IdentityServiceInterface
from app.infrastructure.email.base import EmailService
from app.merge.repository.repository import MergeProofRepository
from app.merge.repository.repository_interface import MergeProofRepositoryInterface
from app.merge.services.merge_service import MergeService
from app.merge.services.merge_service_interface import MergeServiceInterface
from app.merge.services.proof_service import MergeProofService
from app.merge.services.proof_service_interface import MergeProofServiceInterface
from app.two_factor.dependencies import get_email_service, get_two_factor_service
from app.two_factor.repository.repository import TwoFactorRepository
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.username_auth.repository.repository import UsernameIdentityRepository
from app.users.dependencies import get_user_repository, get_user_service
from app.users.repository.repository_interface import UserRepositoryInterface
from app.users.services.service_interface import UserServiceInterface


async def get_merge_proof_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MergeProofRepositoryInterface:
    return MergeProofRepository(session)


async def get_merge_proof_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    merge_proof_repository: Annotated[
        MergeProofRepositoryInterface,
        Depends(get_merge_proof_repository),
    ],
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    user_service: Annotated[
        UserServiceInterface,
        Depends(get_user_service),
    ],
    two_factor_service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
) -> MergeProofServiceInterface:
    return MergeProofService(
        merge_proof_repository,
        user_repository,
        user_service,
        UsernameIdentityRepository(session),
        EmailIdentityRepository(session),
        two_factor_service,
    )


async def get_merge_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    user_service: Annotated[
        UserServiceInterface,
        Depends(get_user_service),
    ],
    identity_service: Annotated[
        IdentityServiceInterface,
        Depends(get_identity_service),
    ],
    merge_proof_repository: Annotated[
        MergeProofRepositoryInterface,
        Depends(get_merge_proof_repository),
    ],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> MergeServiceInterface:
    return MergeService(
        user_repository,
        user_service,
        identity_service,
        TwoFactorRepository(session),
        merge_proof_repository,
        email_service,
    )
