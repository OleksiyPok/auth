# app/auth/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session


from app.core.db import get_session
from app.users.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register/", response_model=UserResponse)
def register_route(user_data: UserCreate, session: Session = Depends(get_session)):
    # try:
    #     return register_user(user_data, session)
    # except ValueError as e:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    pass
