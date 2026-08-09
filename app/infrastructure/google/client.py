# app/infrastructure/google/client.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.infrastructure.google.exceptions import GoogleAPIError


def create_google_people_client(
    credentials: Credentials,
):
    try:
        return build(
            "people",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )
    except Exception as exc:
        raise GoogleAPIError(
            f"Failed to create Google People API client: {exc}"
        ) from exc
