"""
DB schema definitions and operations
"""
from typing import Optional, Union

from datetime import datetime

import sqlalchemy
from databases import Database, DatabaseURL

from . import models
from .settings import settings

metadata = sqlalchemy.MetaData()

account = sqlalchemy.Table(
    "account",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "username", sqlalchemy.String(length=255), unique=True, nullable=False
    ),
    sqlalchemy.Column(
        "password", sqlalchemy.String(length=288), nullable=False
    ),
    # If we'll be using MySQL < 8.0.16, we'll just declare it as unsigned int
    sqlalchemy.Column(
        "balance",
        sqlalchemy.Integer,
        sqlalchemy.CheckConstraint("balance >= 0"),
        nullable=False,
        server_default="0",
    ),
)

transaction = sqlalchemy.Table(
    "transaction",
    metadata,
    sqlalchemy.Column(
        "id", sqlalchemy.String(length=255), nullable=False, primary_key=True
    ),
    sqlalchemy.Column(
        "account_from",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("account.id"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "account_to",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("account.id"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "type", sqlalchemy.Enum(models.TransactionType), nullable=False
    ),
    sqlalchemy.Column("amount", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(
        "created", sqlalchemy.DateTime, nullable=False, index=True
    ),
)


def init_db(engine: sqlalchemy.engine.Engine):
    """
    Create all required tables and insert prerequisite data.
    """
    metadata.create_all(engine)
    with engine.connect() as conn:
        try:
            conn.execute(
                account.insert().values(
                    id=settings.TOPUP_ACCOUNT_ID,
                    username="system:topup",
                    password="",
                )
            )
        except sqlalchemy.exc.IntegrityError:
            pass


class DB:
    """
    `databases` wrapper that implements actual DB operations.
    """

    def __init__(self, db_uri: DatabaseURL, *args, **kwargs):
        self._db = Database(db_uri, *args, **kwargs)

    def __call__(self) -> "DB":
        # Hook for FastAPI dependency injection
        return self

    @property
    def dbapi(self):
        # Shortcut for accessing dialect module, e.g. for handling errors.
        # DBAPI errors can be caught using `db.dbapi.Error` (or one of the more specific errors)
        dbapi = type(self._db._backend._dialect).dbapi()
        if hasattr(dbapi, "err"):
            return dbapi.err
        if hasattr(dbapi, "error"):
            return dbapi.error
        return dbapi

    async def get_account(
        self, id_or_username: Union[int, str]
    ) -> Optional[models.Account]:
        if isinstance(id_or_username, int):
            query = account.select().where(account.c.id == id_or_username)
        else:
            query = account.select().where(account.c.username == id_or_username)
        res = await self._db.fetch_one(query)
        if res is not None:
            return models.Account.parse_obj(res)
        return None

    async def create_account(self, username: str, password: str):
        async with self._db.transaction():
            await self._db.execute(
                account.insert(),
                values={"username": username, "password": password},
            )

    async def create_transaction(
        self,
        id_: str,
        account_from: int,
        account_to: int,
        amount: int,
        type_: models.TransactionType,
    ):
        async with self._db.transaction():
            if type_ is models.TransactionType.transfer:
                await self._db.execute(
                    account.update()
                    .where(account.c.id == account_from)
                    .values(balance=account.c.balance - amount)
                )
            await self._db.execute(
                account.update()
                .where(account.c.id == account_to)
                .values(balance=account.c.balance + amount)
            )
            await self._db.execute(
                transaction.insert(),
                values={
                    "id": id_,
                    "account_from": account_from,
                    "account_to": account_to,
                    "amount": amount,
                    "type": type_,
                    "created": datetime.utcnow().replace(microsecond=0),
                },
            )

    async def get_transaction(
        self, transaction_id: str, account_id: Optional[int] = None
    ) -> Optional[models.Transaction]:
        query = self._transaction_query(for_account=account_id).where(
            transaction.c.id == transaction_id
        )
        res = await self._db.fetch_one(query)
        if res is not None:
            return self._build_transaction_model(res)
        return None

    async def get_transactions(
        self,
        account_id: int,
        dt_from: Optional[datetime] = None,
        dt_to: Optional[datetime] = None,
        limit: Optional[int] = None,
        order: Optional[models.Ordering] = None,
    ) -> list[models.Transaction]:
        query = self._transaction_query(for_account=account_id)

        if dt_from is not None:
            query = query.where(transaction.c.created >= dt_from)
        if dt_to is not None:
            query = query.where(transaction.c.created <= dt_to)
        if limit is not None:
            query = query.limit(limit)
        if order is not None:
            query = query.order_by(
                transaction.c.created.asc()
                if order is models.Ordering.asc
                else transaction.c.created.desc()
            )

        res = await self._db.fetch_all(query)
        return [self._build_transaction_model(row) for row in res]

    # Helpers for selecting transactions

    @staticmethod
    def _transaction_query(
        for_account: Optional[int] = None,
    ) -> sqlalchemy.sql.expression.Select:
        account_from_alias = account.alias()
        account_to_alias = account.alias()
        query = (
            sqlalchemy.sql.select(
                [
                    transaction,
                    account_from_alias.c.username.label(
                        "account_from_username"
                    ),
                    account_to_alias.c.username.label("account_to_username"),
                ]
            )
            .where(
                transaction.c.account_from == account_from_alias.c.id,
            )
            .where(
                transaction.c.account_to == account_to_alias.c.id,
            )
        )
        if for_account is not None:
            query = query.where(
                (transaction.c.account_from == for_account)
                | (transaction.c.account_to == for_account)
            )
        return query

    @staticmethod
    def _build_transaction_model(
        row: sqlalchemy.engine.RowProxy,
    ) -> models.Transaction:
        row = dict(row)
        row["account_from"] = {
            "id": row.pop("account_from"),
            "username": row.pop("account_from_username"),
        }
        row["account_to"] = {
            "id": row.pop("account_to"),
            "username": row.pop("account_to_username"),
        }
        return models.Transaction.construct(**row)
