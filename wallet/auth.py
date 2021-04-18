"""
Helpers for authentication
"""
from typing import Optional

import hashlib
import secrets

from fastapi.security.http import HTTPBasic

from .settings import settings

security = HTTPBasic()


def get_password_hash(password: str, salt: Optional[str] = None) -> str:
    """
    Generate a hash for the password using either the provided salt or a randomly generated one.

    Stores the salt by prepending it to the password hash.
    """
    if salt is None:
        salt = secrets.token_hex(settings.SALT_LENGTH // 2)
    return (
        salt
        + hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
    )


def verify_password_hash(password: str, hash: str) -> bool:
    """
    Securely check that the password's hash is equal to the one that was passed.
    """
    salt = hash[: settings.SALT_LENGTH]
    return secrets.compare_digest(get_password_hash(password, salt), hash)
