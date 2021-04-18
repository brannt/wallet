from typing import Optional

import secrets
from datetime import datetime

from wallet import auth, db, models


async def account(
    db_session: db.DB,
    username: str,
    password: str,
    balance: int = 0,
    id_: int = None,
) -> models.Account:
    values = {
        "username": username,
        "password": auth.get_password_hash(password),
        "balance": balance,
    }
    if id_ is not None:
        values["id"] = id_
    query = db.account.insert()
    id_ = await db_session._db.execute(query, values=values)
    values.setdefault("id", id_)
    return models.Account(**values)


async def transaction(
    db_session: db.DB,
    account_from: int,
    account_to: int,
    type_: models.TransactionType,
    amount: Optional[int] = None,
    id_: Optional[str] = None,
    created: Optional[datetime] = None,
) -> models.Transaction:
    values = {
        "id": id_ if id_ is not None else secrets.token_hex(),
        "created": created
        if created is not None
        else datetime.utcnow().replace(microsecond=0),
        "account_from": account_from,
        "account_to": account_to,
        "type": type_.value,
        "amount": amount if amount is not None else 100,
    }
    query = db.transaction.insert()
    await db_session._db.execute(query, values=values)
    return await db_session.get_transaction(values["id"])
