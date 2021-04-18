"""
Dependency definitions for the FastAPI dependency injection system
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials

from . import auth, models
from .db import DB
from .settings import settings

db = DB(settings.DATABASE_URI)


async def get_current_user(
    db: DB = Depends(db),
    credentials: HTTPBasicCredentials = Depends(auth.security),
) -> models.Account:
    user = await db.get_account(credentials.username)
    if user and auth.verify_password_hash(
        credentials.password, user.password.get_secret_value()
    ):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
