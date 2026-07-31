# app/main.py

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.core.config import settings
from app.db.engine import engine
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting...")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

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


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="debug",
    )
