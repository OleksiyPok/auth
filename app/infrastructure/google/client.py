# app/infrastructure/google/client.py

from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.infrastructure.google.exceptions import GoogleAPIRequestError


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
        raise GoogleAPIRequestError(
            f"Failed to create Google People API client: {exc}"
        ) from exc


def execute_google_request(
    request: Any,
) -> Any:
    try:
        return request.execute()
    except HttpError as exc:
        raise GoogleAPIRequestError(
            f"Google People API returned HTTP {exc.resp.status}"
        ) from exc
