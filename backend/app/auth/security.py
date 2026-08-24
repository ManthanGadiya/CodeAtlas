"""Password hashing and session-token primitives."""

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# Argon2id with library defaults (docs/Security_Privacy_And_Ethics.md §6).
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return bool(_hasher.verify(password_hash, password))
    except (VerifyMismatchError, InvalidHashError):
        return False


def generate_session_token() -> str:
    """Opaque, high-entropy token handed to the browser as a cookie value."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Only the SHA-256 of a token is stored, so a DB leak cannot resurrect sessions."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)
