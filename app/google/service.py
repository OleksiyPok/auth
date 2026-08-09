# app/google/service.py

from datetime import datetime, timedelta, timezone

from googleapiclient.errors import HttpError

from app.google.models import GoogleAccount, GoogleOAuthState
from app.google.repository_interface import GoogleRepositoryInterface
from app.google.schemas import GoogleContactCreateSchema, GoogleContactResponseSchema
from app.google.service_interface import GoogleServiceInterface
from app.infrastructure.google.client import create_google_people_client
from app.infrastructure.google.credentials import (
    credentials_from_account,
    credentials_to_dict,
)
from app.infrastructure.google.exceptions import (
    GoogleAccountAlreadyConnectedError,
    GoogleAccountNotFoundError,
    GoogleAPIError,
    GoogleOAuthStateError,
)
from app.infrastructure.google.oauth import (
    exchange_google_code,
    get_google_authorization_url,
    get_google_user_id,
)
from app.users.models import User

OAUTH_STATE_EXPIRE_MINUTES = 10


class GoogleService(GoogleServiceInterface):

    def __init__(
        self,
        repository: GoogleRepositoryInterface,
    ):
        self._repository = repository

    async def create_authorization_url(
        self,
        user: User,
    ) -> str:
        authorization_url, state, code_verifier = get_google_authorization_url()

        oauth_state = GoogleOAuthState(
            user_id=user.id,
            state=state,
            code_verifier=code_verifier,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=OAUTH_STATE_EXPIRE_MINUTES),
        )

        await self._repository.create_oauth_state(oauth_state)

        return authorization_url

    async def handle_callback(
        self,
        code: str,
        state: str,
    ) -> None:
        oauth_state = await self._repository.get_oauth_state(state)

        if oauth_state is None:
            raise GoogleOAuthStateError()

        if oauth_state.used:
            raise GoogleOAuthStateError()

        if oauth_state.expires_at <= datetime.now(timezone.utc):
            raise GoogleOAuthStateError()

        credentials = exchange_google_code(
            code=code,
            state=state,
            code_verifier=oauth_state.code_verifier,
        )

        await self._repository.mark_oauth_state_used(oauth_state)

        google_user_id = get_google_user_id(credentials)

        existing_account = await self._repository.get_account_by_google_user_id(
            google_user_id,
        )

        if (
            existing_account is not None
            and existing_account.user_id != oauth_state.user_id
        ):
            raise GoogleAccountAlreadyConnectedError()

        data = credentials_to_dict(credentials)

        existing_user_account = await self._repository.get_account_by_user_id(
            oauth_state.user_id,
        )

        if existing_user_account is None:
            account = GoogleAccount(
                user_id=oauth_state.user_id,
                google_user_id=google_user_id,
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                token_expires_at=data["expiry"],
            )

            await self._repository.create_account(account)
            return

        existing_user_account.google_user_id = google_user_id
        existing_user_account.access_token = data["access_token"]
        existing_user_account.refresh_token = data["refresh_token"]
        existing_user_account.token_expires_at = data["expiry"]
        existing_user_account.updated_at = datetime.now(timezone.utc)

        await self._repository.update_account(existing_user_account)

    async def get_contacts(
        self,
        user: User,
    ) -> list[GoogleContactResponseSchema]:
        account = await self._repository.get_account_by_user_id(
            user.id,
        )

        if account is None:
            raise GoogleAccountNotFoundError()

        credentials = credentials_from_account(account)
        client = create_google_people_client(credentials)

        try:
            response = (
                client.people()
                .connections()
                .list(
                    resourceName="people/me",
                    personFields="names,emailAddresses,phoneNumbers",
                    pageSize=100,
                )
                .execute()
            )

        except HttpError as exc:
            raise GoogleAPIError(
                f"Google People API returned HTTP {exc.resp.status}"
            ) from exc

        contacts = []

        for person in response.get("connections", []):
            names = person.get("names", [])
            emails = person.get("emailAddresses", [])
            phones = person.get("phoneNumbers", [])

            display_name = None
            email = None
            phone = None

            if names:
                display_name = names[0].get("displayName")

            if emails:
                email = emails[0].get("value")

            if phones:
                phone = phones[0].get("value")

            contacts.append(
                GoogleContactResponseSchema(
                    resource_name=person["resourceName"],
                    display_name=display_name,
                    email=email,
                    phone=phone,
                )
            )

        return contacts

    async def create_contact(
        self,
        user: User,
        data: GoogleContactCreateSchema,
    ) -> GoogleContactResponseSchema:
        account = await self._repository.get_account_by_user_id(
            user.id,
        )

        if account is None:
            raise GoogleAccountNotFoundError()

        credentials = credentials_from_account(account)
        client = create_google_people_client(credentials)

        person = {
            "names": [
                {
                    "givenName": data.given_name,
                }
            ],
        }

        if data.family_name:
            person["names"][0]["familyName"] = data.family_name

        if data.email:
            person["emailAddresses"] = [
                {
                    "value": data.email,
                }
            ]

        if data.phone:
            person["phoneNumbers"] = [
                {
                    "value": data.phone,
                }
            ]

        try:
            response = (
                client.people()
                .createContact(
                    body=person,
                )
                .execute()
            )

        except HttpError as exc:
            raise GoogleAPIError(
                f"Google People API returned HTTP {exc.resp.status}"
            ) from exc

        names = response.get("names", [])
        emails = response.get("emailAddresses", [])
        phones = response.get("phoneNumbers", [])

        return GoogleContactResponseSchema(
            resource_name=response["resourceName"],
            display_name=(names[0].get("displayName") if names else None),
            email=(emails[0].get("value") if emails else None),
            phone=(phones[0].get("value") if phones else None),
        )
