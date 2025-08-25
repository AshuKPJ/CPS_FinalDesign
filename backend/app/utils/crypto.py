from cryptography.fernet import Fernet, InvalidToken
import os, base64
# NEW: load .env automatically so os.getenv() works in dev
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

_f = None  # lazily initialized

def _get_key_from_settings() -> str | None:
    # Fallback to pydantic settings if available
    try:
        from app.core.config import settings
        return (
            getattr(settings, "CAPTCHA_SECRET_KEY", None)
            or getattr(settings, "CAPTCHA_ENCRYPTION_KEY", None)
        )
    except Exception:
        return None

def _get_fernet():
    global _f
    if _f is not None:
        return _f

    # read from environment first, then settings
    key = os.getenv("CAPTCHA_SECRET_KEY") or os.getenv("CAPTCHA_ENCRYPTION_KEY")
    if not key:
        key = _get_key_from_settings()

    if not key:
        raise RuntimeError("CAPTCHA_SECRET_KEY or CAPTCHA_ENCRYPTION_KEY is not set")

    # normalize quotes/whitespace
    key = key.strip().strip('"').strip("'")

    # validate Fernet key (urlsafe base64, 32 bytes -> 44-char string incl '=')
    try:
        base64.urlsafe_b64decode(key.encode())
    except Exception:
        raise RuntimeError(
            "Invalid CAPTCHA key. Generate one with:\n"
            '  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )

    _f = Fernet(key)
    return _f

def encrypt(cleartext: str) -> str:
    if not cleartext:
        return ""
    f = _get_fernet()
    return f.encrypt(cleartext.encode()).decode()

def decrypt(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        # key changed or value wasn't encrypted previously
        return ""
