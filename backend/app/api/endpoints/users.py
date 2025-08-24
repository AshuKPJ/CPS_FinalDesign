# backend/app/api/endpoints/users.py
from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.db.models.user import User
from app.db import schemas
from app.utils.password import get_password_hash
from app.utils.crypto import encrypt, decrypt

router = APIRouter(prefix="/users", tags=["users"])

# ---- logger ----
logger = logging.getLogger("app.users")

# ──────────────────────────────────────────────────────────────────────────────
# Current user
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=schemas.User)
def me(current_user: User = Depends(get_current_active_user)):
    return current_user

# ──────────────────────────────────────────────────────────────────────────────
# DeathByCaptcha settings
#   User model columns:
#     - captcha_username (text, nullable)
#     - captcha_password_hash (text, nullable)  ← stored via attr captcha_password_encrypted
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/captcha", response_model=schemas.CaptchaView)
def get_captcha_settings(
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    req_id = request.headers.get("x-request-id") or "-"
    try:
        has_user = bool((current_user.captcha_username or "").strip())
        has_secret = bool((current_user.captcha_password_encrypted or "").strip())
        has = has_user and has_secret

        logger.info(
            "GET /users/captcha start req_id=%s user_id=%s email=%s has_user=%s has_secret=%s",
            req_id, current_user.id, current_user.email, has_user, has_secret
        )

        pwd = decrypt(current_user.captcha_password_encrypted) if has else ""
        logger.info(
            "GET /users/captcha ok req_id=%s user_id=%s has=%s pwd_len=%s",
            req_id, current_user.id, has, (len(pwd) if pwd else 0)
        )

        return schemas.CaptchaView(
            has_captcha=has,
            captcha_username=current_user.captcha_username if has else None,
            captcha_password=pwd if has else None,
        )
    except HTTPException:
        # bubble up explicit HTTP errors
        logger.exception("GET /users/captcha http-error req_id=%s user_id=%s", req_id, current_user.id)
        raise
    except Exception as e:
        logger.exception("GET /users/captcha failed req_id=%s user_id=%s", req_id, current_user.id)
        # Do not leak server internals to the client
        raise HTTPException(status_code=500, detail="Failed to load captcha settings") from e


@router.post("/captcha", response_model=schemas.CaptchaView)
def set_captcha_settings(
    payload: schemas.CaptchaUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    req_id = request.headers.get("x-request-id") or "-"
    logger.info(
        "POST /users/captcha start req_id=%s user_id=%s email=%s",
        req_id, current_user.id, current_user.email
    )
    try:
        username = (payload.captcha_username or "").strip()
        password_clear = (payload.captcha_password.get_secret_value() if payload.captcha_password else "").strip()

        if not username or not password_clear:
            logger.warning(
                "POST /users/captcha validation req_id=%s user_id=%s missing_field username=%s pw_len=%s",
                req_id, current_user.id, bool(username), len(password_clear)
            )
            raise HTTPException(status_code=422, detail="captcha_username and captcha_password are required")

        # Encrypt may raise if key missing/invalid → caught below
        encrypted = encrypt(password_clear)

        # Persist
        current_user.captcha_username = username
        current_user.captcha_password_encrypted = encrypted  # maps to captcha_password_hash column
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        logger.info(
            "POST /users/captcha ok req_id=%s user_id=%s stored_len=%s",
            req_id, current_user.id, len(encrypted)
        )
        return schemas.CaptchaView(
            has_captcha=True,
            captcha_username=username,
            captcha_password=password_clear,  # echo back for UI
        )

    except HTTPException:
        # Don’t rollback on 4xx unless we wrote; but safe to rollback anyway
        db.rollback()
        logger.exception("POST /users/captcha http-error req_id=%s user_id=%s", req_id, current_user.id)
        raise
    except Exception as e:
        db.rollback()
        logger.exception("POST /users/captcha failed req_id=%s user_id=%s", req_id, current_user.id)
        raise HTTPException(status_code=500, detail="Failed to save captcha settings") from e

# ──────────────────────────────────────────────────────────────────────────────
# Password reset (token-based)
# ──────────────────────────────────────────────────────────────────────────────

_SECRET = os.getenv("PASSWORD_RESET_SECRET", "change-me")
_EXP_MIN = int(os.getenv("PASSWORD_RESET_EXP_MINUTES", "30"))

def _make_reset_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=_EXP_MIN),
        "iat": datetime.utcnow(),
        "typ": "pwreset",
    }
    return jwt.encode(payload, _SECRET, algorithm="HS256")

def _decode_reset_token(token: str):
    try:
        return jwt.decode(token, _SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset link expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid reset link")

@router.post("/password/request")
def request_password_reset(
    email: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"ok": True}

    token = _make_reset_token(user)
    reset_url = f"{os.getenv('FRONTEND_BASE_URL','http://localhost:3000').rstrip('/')}/reset-password?token={token}"
    return {"ok": True, "reset_url": reset_url}

@router.post("/password/reset")
def reset_password(
    token: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    data = _decode_reset_token(token)
    user_id = data.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    return {"ok": True}
