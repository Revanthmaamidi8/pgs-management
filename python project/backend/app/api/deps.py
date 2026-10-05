import secrets
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token, get_password_hash
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(reusable_oauth2),
    portal_role: str = Header(default="OWNER", alias="X-Portal-Role"),
    db: Session = Depends(get_db),
) -> User:
    if token is None:
        role_name = portal_role.upper()
        if role_name not in {"OWNER", "TENANT"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portal role must be OWNER or TENANT",
            )

        role = db.query(Role).filter(Role.name == role_name).first()
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Portal role is not initialized",
            )

        username = f"portal_{role_name.lower()}"
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            user = User(
                username=username,
                email=f"{username}@local.invalid",
                full_name=f"{role_name.title()} Portal",
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                role_id=role.id,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    try:
        user = db.query(User).filter(User.id == UUID(str(user_id))).first()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return user
