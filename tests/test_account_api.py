import httpx
import pytest
from wallet.auth import get_password_hash
from wallet.db import DB
from wallet.models import Account
from wallet.settings import settings

from . import asserts


@pytest.mark.asyncio
async def test_create_account(client: httpx.AsyncClient, db_session: DB):
    response = await client.post(
        "/account", json={"username": "test", "password": "1q2w3e"}
    )
    assert response.status_code == 201, response.json()

    account = await db_session.get_account("test")
    asserts.model_has_fields(account, username="test", balance=0)
    assert account.password.get_secret_value() == get_password_hash(
        "1q2w3e", account.password.get_secret_value()[: settings.SALT_LENGTH]
    )
    assert response.json() == {
        "id": account.id,
        "username": account.username,
        "balance": account.balance,
    }


@pytest.mark.asyncio
async def test_create_account_existing(
    account: Account, client: httpx.AsyncClient, db_session: DB
):
    account_balance = account.balance
    response = await client.post(
        "/account",
        json={"username": account.username, "password": "new_password"},
    )
    assert response.status_code == 400, response.json()
    account = await db_session.get_account("test")
    # Check the password has not changed
    assert account.password.get_secret_value() == get_password_hash(
        "1q2w3e", account.password.get_secret_value()[: settings.SALT_LENGTH]
    )
    assert account.balance == account_balance


@pytest.mark.asyncio
async def test_create_account_invalid_fields(client: httpx.AsyncClient):
    response = await client.post(
        "/account", json={"username": "", "password": "short"}
    )
    assert response.status_code == 400, response.json()


@pytest.mark.asyncio
async def test_create_account_missing_fields(client: httpx.AsyncClient):
    response = await client.post("/account", json={})
    assert response.status_code == 400, response.json()


@pytest.mark.asyncio
async def test_get_account(account: Account, client: httpx.AsyncClient):
    response = await client.get("/account", auth=account.auth)
    assert response.status_code == 200, response.json()

    assert response.json() == {
        "id": account.id,
        "username": account.username,
        "balance": account.balance,
    }


@pytest.mark.asyncio
async def test_get_no_auth(client: httpx.AsyncClient):
    response = await client.get("/account")
    assert response.status_code == 401, response.json()


@pytest.mark.asyncio
async def test_get_wrong_username(account: Account, client: httpx.AsyncClient):
    response = await client.get("/account", auth=("unknown", account.auth[1]))
    assert response.status_code == 401, response.json()


@pytest.mark.asyncio
async def test_get_wrong_password(account: Account, client: httpx.AsyncClient):
    response = await client.get("/account", auth=(account.auth[0], "unknown"))
    assert response.status_code == 401, response.json()
