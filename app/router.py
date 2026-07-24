# app/router.py

from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.core.config import settings
from app.sessions.router import router as sessions_router
from app.users.router import router as users_router

router = APIRouter(prefix=settings.API_V1_PREFIX)

router.include_router(auth_router)
router.include_router(sessions_router)
router.include_router(users_router)
