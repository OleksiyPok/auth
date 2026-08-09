# app/main.py

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlmodel import SQLModel

from app.bootstrap.superadmin import create_initial_superadmin
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.db.engine import engine
from app.db.session import session_factory
from app.google.models import GoogleAccount, GoogleOAuthState
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting...")

    async with engine.begin() as conn:
        database_is_new = await conn.run_sync(
            lambda sync_conn: len(inspect(sync_conn).get_table_names()) == 0
        )
        await conn.run_sync(SQLModel.metadata.create_all)

    if database_is_new:
        async with session_factory() as session:
            await create_initial_superadmin(session)

    yield

    print("App shutting down...")

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    swagger_ui_parameters={
        "docExpansion": "none",
        # "tagsSorter": "alpha",
        # "operationsSorter": "none",
        # "operationsSorter": "method",
        # "operationsSorter": "alpha",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="debug",
    )
