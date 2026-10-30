# app/core/openapi.py

"""Tag order and descriptions for Swagger / OpenAPI.

The `name` of a tag must match the tag used in the routers exactly.
"""

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "Username Authentication",
        "description": "Register and sign in with a username and password.",
    },
    {
        "name": "Email Authentication",
        "description": (
            "Register with email confirmation by a one-time code, and sign in "
            "with email and password."
        ),
    },
    {
        "name": "Google Authentication",
        "description": (
            "Sign in with a Google account (OAuth 2.0). `login` returns the "
            "Google authorization URL; `callback` is called by Google after the "
            "user signs in."
        ),
    },
    {
        "name": "Two-Factor Login",
        "description": (
            "Second step of sign-in for accounts with two-factor authentication "
            "enabled: confirm the login challenge with a one-time code. "
            "No access token is needed; the challenge id from the login "
            "response is used."
        ),
    },
    {
        "name": "Auth",
        "description": (
            "Token lifecycle: refresh an access token and log out. "
            "Refresh tokens are rotated on every use."
        ),
    },
    {
        "name": "Account",
        "description": (
            "Actions of the signed-in user on their own account: view, update "
            "and deactivate."
        ),
    },
    {
        "name": "Two-Factor Settings",
        "description": (
            "Two-factor authentication of the current user: view the status "
            "and methods, enable and disable it with a confirmation code."
        ),
    },
    {
        "name": "Identities",
        "description": (
            "Sign-in methods of the current user (username, email, Google): "
            "list them and link new ones."
        ),
    },
    {
        "name": "Sessions",
        "description": "Active sessions of the current user: list and revoke.",
    },
    {
        "name": "User Management",
        "description": (
            "Actions on other users: list, view, assign roles, deactivate and "
            "purge. Access is controlled by permissions."
        ),
    },
    {
        "name": "Health",
        "description": "Service liveness and readiness checks. No authentication.",
    },
    {
        "name": "Development",
        "description": "Development tools. Superadmin and admin only.",
    },
]