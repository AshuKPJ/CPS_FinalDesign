from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from app.core.config import settings
from app.core import security
from app.db.database import get_db
from app.db import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

class TokenData(BaseModel):
    sub: Optional[str] = None

def _extract_token(request: Request, header_token: Optional[str]) -> str:
    if header_token:
        return header_token
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return ""

def _maybe_uuid(s: str):
    try:
        return UUID(s)
    except Exception:
        return s

def get_current_user(request: Request, db=Depends(get_db), header_token: Optional[str] = Depends(oauth2_scheme)) -> models.User:
    token = _extract_token(request, header_token)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenData(**payload)
        if not token_data.sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = _maybe_uuid(token_data.sub)
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not getattr(current_user, "is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
