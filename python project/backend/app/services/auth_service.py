from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister


def ensure_default_roles(db: Session) -> dict[str, Role]:
    roles: dict[str, Role] = {}

    for role_name in ("SUPER_ADMIN", "OWNER", "TENANT"):
        role = db.query(Role).filter(Role.name == role_name).first()
        if role is None:
            role = Role(name=role_name, description=f"{role_name} access role")
            db.add(role)
            db.flush()
        roles[role_name] = role

    db.commit()
    return roles


def register_user(db: Session, payload: UserRegister) -> User:
    roles = ensure_default_roles(db)

    if db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists.",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role_id=roles["OWNER"].id,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: UserLogin) -> User:
    normalized_value = payload.username_or_email.strip()
    user = db.query(User).filter(
        (User.username == normalized_value) | (User.email == normalized_value)
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    return user


def generate_token_for_user(user: User) -> Token:
    token = create_access_token({"user_id": str(user.id), "username": user.username, "role": user.role.name})
    return Token(access_token=token)


def get_user_by_id(db: Session, user_id: str) -> User | None:
    try:
        return db.query(User).filter(User.id == UUID(user_id)).first()
    except ValueError:
        return None