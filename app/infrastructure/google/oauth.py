# app/infrastructure/google/oauth.py

from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from app.core.config import settings
from app.infrastructure.google.config import GOOGLE_OAUTH_SCOPES
from app.infrastructure.google.exceptions import GoogleOAuthError


def create_google_oauth_flow(
    code_verifier: str | None = None,
) -> Flow:
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=GOOGLE_OAUTH_SCOPES,
        code_verifier=code_verifier,
    )

    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    return flow


def get_google_authorization_url() -> tuple[str, str, str]:
    try:
        flow = create_google_oauth_flow()

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )

        return (
            authorization_url,
            state,
            flow.code_verifier,
        )

    except Exception as exc:
        raise GoogleOAuthError(
            f"Failed to create Google authorization URL: {exc}"
        ) from exc


def exchange_google_code(
    code: str,
    state: str,
    code_verifier: str,
):
    try:
        flow = create_google_oauth_flow(
            code_verifier=code_verifier,
        )

        flow.state = state

        flow.fetch_token(
            code=code,
            code_verifier=code_verifier,
        )

        return flow.credentials

    except Exception as exc:
        raise GoogleOAuthError(
            f"Failed to exchange Google authorization code: {exc}"
        ) from exc


def get_google_user_id(credentials) -> str:
    try:
        if not credentials.id_token:
            raise GoogleOAuthError("Google OAuth response does not contain id_token")

        token_info = id_token.verify_oauth2_token(
            credentials.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        google_user_id = token_info.get("sub")

        if not google_user_id:
            raise GoogleOAuthError("Google ID token does not contain subject")

        return google_user_id

    except GoogleOAuthError:
        raise
    except Exception as exc:
        raise GoogleOAuthError(f"Failed to verify Google ID token: {exc}") from exc
