from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.services.auth_service import authenticate_user, generate_token_for_user, register_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, payload)
    user.role
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    return generate_token_for_user(user)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )
