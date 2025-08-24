# backend/app/api/endpoints/auth.py
from __future__ import annotations

import os
from datetime import timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.api import deps
from app.log_stream import log
from app.db.models.user import User as UserModel
from app.core import security

# ------------------------ Settings fallback ------------------------
# If you already have settings in app.core.settings, we'll use them.
try:
    from app.core.settings import settings  # type: ignore
except Exception:  # pragma: no cover
    class _Fallback:
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    settings = _Fallback()  # type: ignore

# ------------------------ Pydantic models -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr | str = Field(...)
    password: str = Field(..., min_length=1)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class UserOut(BaseModel):
    id: str | int
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

# ------------------------ Helpers -------------------------

def _pyd_parse(cls, data: Dict[str, Any]):
    """
    Pydantic v2 (model_validate) with v1 fallback (parse_obj).
    """
    try:
        return cls.model_validate(data)  # type: ignore[attr-defined]
    except AttributeError:
        return cls.parse_obj(data)       # type: ignore[attr-defined]

async def _read_json_or_form(request: Request) -> Dict[str, Any]:
    """
    Read request body as JSON first; fall back to form.
    Always return a dict (possibly empty).
    """
    # Try JSON
    try:
        data = await request.json()
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Fall back to form
    try:
        form = await request.form()
        return dict(form)
    except Exception:
        return {}

# ------------------------ Router -------------------------

router = APIRouter(tags=["Auth"])

# -------- Register --------
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(deps.get_db)):
    """
    Create a new user account. Expects JSON body:
    { email, password, first_name?, last_name? }
    """
    existing = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = security.get_password_hash(payload.password)
    user = UserModel(
        email=str(payload.email).lower(),
        hashed_password=hashed,
        first_name=(payload.first_name or "").strip(),
        last_name=(payload.last_name or "").strip(),
        is_active=True,  # if your model has this column
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(
        id=user.id,
        email=user.email,
        first_name=getattr(user, "first_name", "") or "",
        last_name=getattr(user, "last_name", "") or "",
    )

# -------- Login --------
@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(request: Request, db: Session = Depends(deps.get_db)):
    """
    Robust login that accepts JSON or form:
    JSON: { "email": "...", "password": "..." }
    FORM:  email=...&password=...
    """
    log("POST /auth/login hit")

    body = await _read_json_or_form(request)
    if not body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")

    # Pydantic-parse with v2/v1 compatibility
    try:
        payload = _pyd_parse(LoginRequest, body)
    except Exception:
        # Allow username alias
        alias = {
            "email": body.get("email") or body.get("username"),
            "password": body.get("password"),
        }
        try:
            payload = _pyd_parse(LoginRequest, alias)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email and password are required")

    email = (payload.email or "").strip().lower()
    password = payload.password

    user: Optional[UserModel] = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not security.verify_password(password, getattr(user, "hashed_password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    access_token_expires = timedelta(minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    token = security.create_access_token(subject=str(user.id), expires_delta=access_token_expires)

    return Token(access_token=token, token_type="bearer")
