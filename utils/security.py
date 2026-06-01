import hashlib
import os


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with random salt."""
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against the stored hash."""
    try:
        salt, hashed = stored.split(":", 1)
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except Exception:
        return False
