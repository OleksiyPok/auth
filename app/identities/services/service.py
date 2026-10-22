# app/identities/services/service.py

from app.core.identifiers import normalize_username
from app.email_auth.models import EmailIdentity
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.google_auth.models import GoogleIdentity
from app.google_auth.repository.repository_interface import (
    GoogleAuthRepositoryInterface,
)
from app.identities.exceptions import (
    IdentityAlreadyOwnedError,
    IdentityConflictError,
    IdentityTypeConflictError,
)
from app.identities.services.service_interface import IdentityServiceInterface
from app.identities.types import IdentityType
from app.infrastructure.password import hash_password
from app.username_auth.models import UsernameIdentity
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)


def _identity_type(
    identity: EmailIdentity | UsernameIdentity | GoogleIdentity,
) -> IdentityType:
    if isinstance(identity, EmailIdentity):
        return IdentityType.EMAIL
    if isinstance(identity, UsernameIdentity):
        return IdentityType.USERNAME
    if isinstance(identity, GoogleIdentity):
        return IdentityType.GOOGLE
    raise TypeError(f"Unsupported identity: {type(identity).__name__}")


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

    async def list_identities(
        self,
        user_id: str,
    ) -> list[EmailIdentity | UsernameIdentity | GoogleIdentity]:
        identities: list[EmailIdentity | UsernameIdentity | GoogleIdentity] = []

        email_identity = await self._email_repository.get_by_user_id(user_id)
        if email_identity is not None:
            identities.append(email_identity)

        username_identity = await self._username_repository.get_by_user_id(user_id)
        if username_identity is not None:
            identities.append(username_identity)

        google_identity = await self._google_repository.get_identity_by_user_id(user_id)
        if google_identity is not None:
            identities.append(google_identity)

        return identities

    async def get_identity(
        self,
        identity_id: str,
    ) -> EmailIdentity | UsernameIdentity | GoogleIdentity | None:
        """Find an identity of any type by its id, or None if it does not exist."""
        email_identity = await self._email_repository.get_by_id(identity_id)
        if email_identity is not None:
            return email_identity

        username_identity = await self._username_repository.get_by_id(identity_id)
        if username_identity is not None:
            return username_identity

        return await self._google_repository.get_identity_by_id(identity_id)

    async def delete_identity(
        self,
        identity: EmailIdentity | UsernameIdentity | GoogleIdentity,
    ) -> None:
        if isinstance(identity, EmailIdentity):
            await self._email_repository.delete(identity)
        elif isinstance(identity, UsernameIdentity):
            await self._username_repository.delete(identity)
        elif isinstance(identity, GoogleIdentity):
            await self._google_repository.delete_identity(identity)
        else:
            raise TypeError(f"Unsupported identity: {type(identity).__name__}")

    async def transfer_identity(
        self,
        identity: EmailIdentity | UsernameIdentity | GoogleIdentity,
        new_user_id: str,
    ) -> EmailIdentity | UsernameIdentity | GoogleIdentity:
        """Change the owner of the identity.

        Raises IdentityAlreadyOwnedError when the identity already belongs to
        the new owner, and IdentityTypeConflictError when the new owner already
        has an identity of the same type.
        """
        # Transferring to the current owner changes nothing. Callers (Merge,
        # Split) never do it on purpose, so it is reported as an error instead
        # of a silent no-op, and it is checked first so that it is not
        # mistaken for a type conflict with the identity's own owner.
        if identity.user_id == new_user_id:
            raise IdentityAlreadyOwnedError()

        if isinstance(identity, EmailIdentity):
            if await self._email_repository.get_by_user_id(new_user_id) is not None:
                raise IdentityTypeConflictError()
            identity.user_id = new_user_id
            return await self._email_repository.update(identity)

        if isinstance(identity, UsernameIdentity):
            if await self._username_repository.get_by_user_id(new_user_id) is not None:
                raise IdentityTypeConflictError()
            identity.user_id = new_user_id
            return await self._username_repository.update(identity)

        if isinstance(identity, GoogleIdentity):
            if (
                await self._google_repository.get_identity_by_user_id(new_user_id)
                is not None
            ):
                raise IdentityTypeConflictError()
            identity.user_id = new_user_id
            return await self._google_repository.update_identity(identity)

        raise TypeError(f"Unsupported identity: {type(identity).__name__}")

    async def get_type_conflicts(
        self,
        first_user_id: str,
        second_user_id: str,
    ) -> list[IdentityType]:
        """Return the identity types that both users have, in a fixed order.

        A non-empty result is a type conflict and blocks Merge.
        """
        first_types = {
            _identity_type(identity)
            for identity in await self.list_identities(first_user_id)
        }
        second_types = {
            _identity_type(identity)
            for identity in await self.list_identities(second_user_id)
        }

        return [t for t in IdentityType if t in first_types and t in second_types]

    async def link_username(
        self,
        user_id: str,
        username: str,
        password: str,
    ) -> UsernameIdentity:
        """Add a username identity to the user.

        Raises IdentityTypeConflictError when the user already has one, and
        IdentityConflictError when the username belongs to another identity.
        """
        normalized = normalize_username(username)

        if await self._username_repository.get_by_user_id(user_id) is not None:
            raise IdentityTypeConflictError()

        if await self._username_repository.get_by_username(normalized) is not None:
            raise IdentityConflictError()

        identity = UsernameIdentity(
            user_id=user_id,
            username=normalized,
            password_hash=hash_password(password),
        )

        return await self._username_repository.create(identity)
