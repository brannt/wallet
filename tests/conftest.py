from typing import Coroutine, Generator

import asyncio

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from wallet import models
from wallet.db import DB, init_db
from wallet.deps import db
from wallet.main import app
from wallet.settings import settings

from . import factories

pytest.register_assert_rewrite("tests.asserts")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db() -> Generator[DB, None, None]:
    url = settings.TEST_DATABASE_URI
    # Databases uses PyMySQL by default, while SQLAlchemy uses MySQLdb. We have to pass the driver explicitly
    sqlalchemy_url = url.replace("mysql://", "mysql+pymysql://")
    engine = create_engine(sqlalchemy_url)
    if database_exists(sqlalchemy_url):
        drop_database(sqlalchemy_url)
    create_database(sqlalchemy_url)
    init_db(engine)
    yield DB(url, force_rollback=True)
    drop_database(sqlalchemy_url)


@pytest.fixture
async def client(test_db: DB) -> Generator[httpx.AsyncClient, None, None]:
    app.dependency_overrides[db] = test_db
    async with httpx.AsyncClient(app=app, base_url="http://test") as cl:
        yield cl


@pytest.fixture
async def db_session(test_db: DB) -> Generator[DB, None, None]:
    try:
        await test_db._db.connect()
        async with test_db._db.transaction(force_rollback=True):
            yield test_db
    finally:
        await test_db._db.disconnect()


@pytest.fixture
async def account(db_session: DB) -> models.Account:
    username = "test"
    password = "1q2w3e"
    acc = await factories.account(db_session, username, password, balance=1000)
    # Providing an easy way to authorize the account in the API
    acc.__dict__["auth"] = (username, password)
    return acc


@pytest.fixture
async def second_account(db_session: DB) -> models.Account:
    username = "test2"
    password = "123456"
    acc = await factories.account(db_session, username, password, balance=1000)
    return acc
