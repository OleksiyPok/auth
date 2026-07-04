# app/main.py

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel

# from app.auth.router import router as registration_router

# from app.core.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting...")
    # SQLModel.metadata.create_all(engine)
    yield
    print("App shutting down...")


app = FastAPI(
    title="Fast API", lifespan=lifespan, swagger_ui_parameters={"docExpansion": "none"}
)


# app.include_router(registration_router)


if __name__ == "__main__":
    # Important: disable reload while debugging
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="debug",
    )
