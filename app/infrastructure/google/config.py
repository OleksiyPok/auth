# app/infrastructure/google/config.py

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

GOOGLE_CONTACTS_SCOPE = "https://www.googleapis.com/auth/contacts"

GOOGLE_OAUTH_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    GOOGLE_CONTACTS_SCOPE,
]
