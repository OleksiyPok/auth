# app/auth/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.schemas import RegisterRequestSchema, RegisterResponseSchema
from app.db.session import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register/",
    summary="Register user account",
    description="Creates a new user account.",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def register_route(data: RegisterRequestSchema, session: Session = Depends(get_session)):
    # print(user_data.model_dump_json(indent=2))
    try:
        return {
            "id": "a267",  # debug
            "username": data.username,  # debug
            "email": data.email,  # debug
        }
        # return register_user(user_data, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    # pass
