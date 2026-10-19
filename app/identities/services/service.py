# app/identities/services/service.py

from app.email_auth.models import EmailIdentity
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.google_auth.models import GoogleIdentity
from app.google_auth.repository.repository_interface import (
    GoogleAuthRepositoryInterface,
)
from app.identities.services.service_interface import IdentityServiceInterface
from app.identities.types import IdentityType
from app.username_auth.models import UsernameIdentity
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)


class IdentityService(IdentityServiceInterface):
    """Common actions over the identities of all three types."""

    def __init__(
        self,
        email_repository: EmailIdentityRepositoryInterface,
        username_repository: UsernameIdentityRepositoryInterface,
        google_repository: GoogleAuthRepositoryInterface,
    ):
        self._email_repository = email_repository
        self._username_repository = username_repository
        self._google_repository = google_repository

    async def get_owner_id(
        self,
        identity_type: str,
        identity_id: str,
    ) -> str | None:
        """Return the id of the user who owns the identity, or None if it does not exist."""
        identity: EmailIdentity | UsernameIdentity | GoogleIdentity | None

        if identity_type == IdentityType.EMAIL:
            identity = await self._email_repository.get_by_id(identity_id)
        elif identity_type == IdentityType.USERNAME:
            identity = await self._username_repository.get_by_id(identity_id)
        elif identity_type == IdentityType.GOOGLE:
            identity = await self._google_repository.get_identity_by_id(identity_id)
        else:
            return None

        return identity.user_id if identity else None