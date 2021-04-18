import httpx
import pytest
from wallet.db import DB
from wallet.models import Account, TransactionType
from wallet.settings import settings

from . import asserts, factories


@pytest.mark.asyncio
async def test_create_transfer(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    response = await client.put(
        "/transactions/transid",
        json={
            "account_to": {"id": second_account.id},
            "amount": 100,
            "type": "transfer",
        },
        auth=account.auth,
    )

    assert response.status_code == 201, response.json()

    asserts.model_has_fields(await db_session.get_account("test"), balance=900)
    asserts.model_has_fields(
        await db_session.get_account("test2"), balance=1100
    )

    asserts.model_has_fields(
        await db_session.get_transaction("transid"),
        account_from={"id": account.id, "username": account.username},
        account_to={
            "id": second_account.id,
            "username": second_account.username,
        },
        type=TransactionType.transfer,
        amount=100,
    )


@pytest.mark.asyncio
async def test_create_transfer_with_username(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    response = await client.put(
        "/transactions/transid",
        json={
            "account_to": {"username": second_account.username},
            "amount": 100,
            "type": "transfer",
        },
        auth=account.auth,
    )

    assert response.status_code == 201, response.json()

    asserts.model_has_fields(await db_session.get_account("test"), balance=900)
    asserts.model_has_fields(
        await db_session.get_account("test2"), balance=1100
    )

    asserts.model_has_fields(
        await db_session.get_transaction("transid"),
        account_from={"id": account.id, "username": account.username},
        account_to={
            "id": second_account.id,
            "username": second_account.username,
        },
        type=TransactionType.transfer,
        amount=100,
    )


@pytest.mark.asyncio
async def test_create_topup(
    account: Account, client: httpx.AsyncClient, db_session: DB
):
    response = await client.put(
        "/transactions/transid",
        json={
            "amount": 100,
            "type": "topup",
        },
        auth=account.auth,
    )

    assert response.status_code == 201, response.json()

    asserts.model_has_fields(await db_session.get_account("test"), balance=1100)

    asserts.model_has_fields(
        await db_session.get_transaction("transid"),
        account_from={
            "id": settings.TOPUP_ACCOUNT_ID,
            "username": "system:topup",
        },
        account_to={"id": account.id, "username": account.username},
        type=TransactionType.topup,
        amount=100,
    )


@pytest.mark.asyncio
async def test_create_repeated_transaction(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    transaction = await factories.transaction(
        db_session, account.id, second_account.id, TransactionType.transfer, 100
    )
    response = await client.put(
        f"/transactions/{transaction.id}",
        json={
            "account_to": {"id": second_account.id},
            "amount": 100,
            "type": "transfer",
        },
        auth=account.auth,
    )

    asserts.model_has_fields(
        await db_session.get_account("test"), balance=account.balance
    )
    asserts.model_has_fields(
        await db_session.get_account("test2"), balance=second_account.balance
    )


@pytest.mark.asyncio
async def test_create_different_transaction_same_id(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    transaction = await factories.transaction(
        db_session, account.id, second_account.id, TransactionType.transfer, 100
    )
    response = await client.put(
        f"/transactions/{transaction.id}",
        json={
            "amount": 200,
            "type": "topup",
        },
        auth=account.auth,
    )
    assert response.status_code == 400, response.json()

    asserts.model_has_fields(
        await db_session.get_account("test"), balance=account.balance
    )
    asserts.model_has_fields(
        await db_session.get_account("test2"), balance=second_account.balance
    )
    asserts.model_has_fields(
        await db_session.get_transaction(transaction.id),
        account_from={"id": account.id, "username": account.username},
        account_to={
            "id": second_account.id,
            "username": second_account.username,
        },
        type=TransactionType.transfer,
        amount=100,
    )


@pytest.mark.asyncio
async def test_cannot_transfer_to_system_account(
    account: Account, client: httpx.AsyncClient, db_session: DB
):
    response = await client.put(
        "/transactions/transid",
        json={
            "account_to": {"id": settings.TOPUP_ACCOUNT_ID},
            "amount": 100,
            "type": "transfer",
        },
        auth=account.auth,
    )

    assert response.status_code == 400, response.json()
    assert await db_session.get_transaction("transid") is None
    asserts.model_has_fields(
        await db_session.get_account("test"), balance=account.balance
    )


@pytest.mark.asyncio
async def test_cannot_create_transaction_over_balance(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    response = await client.put(
        "/transactions/transid2",
        json={
            "account_to": {"username": second_account.username},
            "amount": account.balance + 1,
            "type": "transfer",
        },
        auth=account.auth,
    )

    assert response.status_code == 400, response.json()
    assert await db_session.get_transaction("transid2") is None
    asserts.model_has_fields(
        await db_session.get_account("test"), balance=account.balance
    )
    asserts.model_has_fields(
        await db_session.get_account("test2"), balance=second_account.balance
    )


@pytest.mark.asyncio
async def test_cannot_create_transaction_negative(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    response = await client.put(
        "/transactions/transid",
        json={
            "account_to": {"username": second_account.username},
            "amount": -1,
            "type": "transfer",
        },
        auth=account.auth,
    )

    assert response.status_code == 400, response.json()
    assert await db_session.get_transaction("transid") is None
    asserts.model_has_fields(
        await db_session.get_account("test"), balance=account.balance
    )
    asserts.model_has_fields(
        await db_session.get_account("test2"), balance=second_account.balance
    )


@pytest.mark.asyncio
async def test_cannot_create_transaction_to_unknown_user(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    response = await client.put(
        "/transactions/transid",
        json={
            "account_to": {"id": 100500},
            "amount": 100,
            "type": "transfer",
        },
        auth=account.auth,
    )

    assert response.status_code == 400, response.json()
    assert await db_session.get_transaction("transid") is None
    asserts.model_has_fields(
        await db_session.get_account("test"), balance=account.balance
    )
    asserts.model_has_fields(
        await db_session.get_account("test2"), balance=second_account.balance
    )


@pytest.mark.asyncio
async def test_cannot_create_transaction_to_unknown_user_by_username(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    response = await client.put(
        "/transactions/transid",
        json={
            "account_to": {"username": "whatever"},
            "amount": 100,
            "type": "transfer",
        },
        auth=account.auth,
    )

    assert response.status_code == 400, response.json()
    assert await db_session.get_transaction("transid") is None
    asserts.model_has_fields(
        await db_session.get_account("test"), balance=account.balance
    )
