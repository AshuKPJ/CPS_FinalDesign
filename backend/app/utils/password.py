
# backend/app/utils/password.py

from passlib.context import CryptContext
from app.core.security import get_password_hash as hash_password, verify_password

# bcrypt is the most common default
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a plain password for storage in DB.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
