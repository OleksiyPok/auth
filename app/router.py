# app/router.py

from fastapi import APIRouter

from app.auth.router import router as registration_router
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

router.include_router(registration_router)
