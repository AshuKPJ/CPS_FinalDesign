from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.database import get_db
from app.db.models.user import User as UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _to_uuid(val: str):
    try:
        return UUID(val)
    except Exception:
        return val  # fall back to raw string


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        # ❗ python-jose does NOT support `leeway=` kwarg; remove it
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_aud": False},
        )
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        user_id = _to_uuid(sub)
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    return current_user


def get_current_admin_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role not in ("admin", "owner"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return current_user


def get_current_owner_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner only")
    return current_user
