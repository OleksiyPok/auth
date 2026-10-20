# app/core/identifiers.py

"""Single place for identifier normalization and display masking.

Every identifier is normalized before it is stored or looked up, so that
different spellings of the same identifier are the same identifier.
"""


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def normalize_username(value: str) -> str:
    # `Admin`, `   Admin   ` and `adMin` are the same username.
    # Allowed characters and inner spaces are a separate validation task.
    return value.strip().casefold()


def mask_email(email: str) -> str:
    # Shown instead of the full address: `john@example.com` -> `j***@example.com`.
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}"
