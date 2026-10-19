# app/core/identifiers.py

"""Single place for identifier normalization.

Every identifier is normalized before it is stored or looked up, so that
different spellings of the same identifier are the same identifier.
"""


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def normalize_username(value: str) -> str:
    # `Admin`, `   Admin   ` and `adMin` are the same username.
    # Allowed characters and inner spaces are a separate validation task.
    return value.strip().casefold()