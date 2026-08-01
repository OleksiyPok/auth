# app/core/exception_handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


async def app_exception_handler(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, AppError)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_exception_handler)
