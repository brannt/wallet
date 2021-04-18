"""
App-specific types and Pydantic models
"""
from typing import Optional

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, constr, validator
from pydantic.types import NonNegativeInt, PositiveInt, SecretStr

Username = constr(min_length=1, max_length=255)


class AccountBase(BaseModel):
    id: Optional[int] = None
    username: Optional[Username] = None

    @validator("username")
    def check_id_or_username(cls, username, values):
        if "id" not in values and not username:
            raise ValueError("either id or username is required")
        return username


class AccountCreate(BaseModel):
    username: Username
    password: SecretStr


class AccountResponse(BaseModel):
    id: int
    username: Username
    balance: NonNegativeInt


class Account(BaseModel):
    id: int
    username: Username
    balance: NonNegativeInt
    password: SecretStr


class TransactionType(Enum):
    topup = "topup"
    transfer = "transfer"


class Ordering(Enum):
    desc = "desc"
    asc = "asc"


class TransactionCreate(BaseModel):
    account_to: Optional[AccountBase] = None
    amount: PositiveInt
    type: TransactionType


class Transaction(TransactionCreate):
    id: constr(min_length=1, max_length=255)
    created: datetime
    account_from: AccountBase
