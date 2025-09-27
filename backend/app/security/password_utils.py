import hashlib
import secrets
from passlib.context import CryptContext

# Try bcrypt first, fallback to scrypt if bcrypt fails
pwd_context = CryptContext(schemes=["scrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt or scrypt as fallback"""
    # Ensure password is within bcrypt's 72-byte limit
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)