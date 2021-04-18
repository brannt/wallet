import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)

    DATABASE_URI: str = "sqlite:///db.sqlite3"
    TEST_DATABASE_URI: str = "sqlite:///testdb.sqlite3"

    SALT_LENGTH = 32

    TOPUP_ACCOUNT_ID = 1

    class Config:
        case_sensitive = True


settings = Settings()
