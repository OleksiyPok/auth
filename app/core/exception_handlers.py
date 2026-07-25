# app/core/exception_handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.core.exceptions import DomainError


async def domain_error_handler(
    _request: Request,
    exc: Exception,
) -> Response:
    if not isinstance(exc, DomainError):
        raise exc

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
