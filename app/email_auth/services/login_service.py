from app.email_auth.exceptions import InvalidEmailCredentialsError
from app.email_auth.repository.repository_interface import EmailIdentityRepositoryInterface
from app.email_auth.schemas import EmailLoginRequestSchema
from app.email_auth.services.login_service_interface import EmailLoginServiceInterface
from app.infrastructure.password import verify_password
from app.sessions.schemas import AuthenticationResponseSchema
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.exceptions import UserNotFoundError
from app.users.repository.repository_interface import UserRepositoryInterface


class EmailLoginService(EmailLoginServiceInterface):

    def __init__(
        self,
        email_identity_repository: EmailIdentityRepositoryInterface,
        user_repository: UserRepositoryInterface,
        two_factor_service: TwoFactorServiceInterface,
    ):
        self._email_identity_repository = email_identity_repository
        self._user_repository = user_repository
        self._two_factor_service = two_factor_service

    async def login(
        self,
        data: EmailLoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema:
        email = data.email.strip().casefold()

        identity = await self._email_identity_repository.get_by_email(email)

        if not identity or not verify_password(
            data.password,
            identity.password_hash,
        ):
            raise InvalidEmailCredentialsError()

        user = await self._user_repository.get_by_id(identity.user_id)

        if not user:
            raise UserNotFoundError()

        two_factor_enabled = await self._two_factor_service.is_enabled(
            user.id,
            "email",
        )

        return await self._two_factor_service.authenticate_or_challenge(
            user=user,
            provider="email",
            two_factor_enabled=two_factor_enabled,
            ip_address=ip_address,
            user_agent=user_agent,
        )
