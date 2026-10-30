# app/main.py

import asyncio
from contextlib import asynccontextmanager, suppress

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlmodel import SQLModel

from app.bootstrap.superadmin import create_initial_superadmin_if_no_users
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.openapi import OPENAPI_TAGS
from app.db.engine import engine
from app.db.session import session_factory
from app.health.router import router as health_router
from app.maintenance.cleanup import run_cleanup_loop
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting...")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with session_factory() as session:
        await create_initial_superadmin_if_no_users(session)

    cleanup_task = asyncio.create_task(
        run_cleanup_loop(settings.CLEANUP_INTERVAL_SECONDS)
    )

    yield

    print("App shutting down...")

    cleanup_task.cancel()
    with suppress(asyncio.CancelledError):
        await cleanup_task

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    swagger_ui_parameters={
        "docExpansion": "none",
        # "tagsSorter": "alpha",
        # "operationsSorter": "none",
        # "operationsSorter": "method",
        # "operationsSorter": "alpha",
    },
)

original_openapi = app.openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = original_openapi()

    components = openapi_schema.setdefault("components", {})

    components["securitySchemes"] = {
        "Username Authentication": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/username/login",
                },
            },
        },
        "Email Authentication": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/email/login",
                },
            },
        },
        "Authentication": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Access token used to access protected resources.",
        },
    }

    app.openapi_schema = openapi_schema

    return openapi_schema


app.openapi = custom_openapi


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_exception_handlers(app)

app.include_router(router)
app.include_router(health_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
        log_level="debug",
    )
