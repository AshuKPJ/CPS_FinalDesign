# backend/app/api/deps.py

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.core import security
from app.core.config import settings
from app.db.database import get_db

# ✅ Use direct path for login token (your project doesn't use /v1/)
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ✅ Updated TokenData schema to support `sub`
class TokenData(BaseModel):
    sub: Optional[str] = None  # <- used to extract user.id from token


# ✅ Main user dependency
def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenData(**payload)

        if not token_data.sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID (sub)",
            )

        user = db.query(models.User).filter(models.User.id == token_data.sub).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_owner_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if current_user.role != "owner":
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
