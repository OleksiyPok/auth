
# app/health/router.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.engine import engine

router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable"},
        )

    return {"status": "ok"}
