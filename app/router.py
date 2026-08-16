# app/router.py

from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.core.config import settings
from app.email_auth.router import router as email_auth_router
from app.google_auth.router import router as google_auth_router
from app.local_auth.router import router as local_auth_router
from app.sessions.router import router as sessions_router
from app.users.router import router as users_router
from app.infrastructure.email.test_message_router import router as test_message_router

router = APIRouter(
    prefix=settings.API_V1_PREFIX,
)

router.include_router(auth_router)
router.include_router(local_auth_router)
router.include_router(email_auth_router)
router.include_router(google_auth_router)
router.include_router(sessions_router)
router.include_router(users_router)

router.include_router(test_message_router)