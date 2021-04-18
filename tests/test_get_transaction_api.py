from datetime import datetime

import httpx
import pytest
from wallet.db import DB
from wallet.models import Account, TransactionType
from wallet.settings import settings

from . import factories


@pytest.mark.asyncio
async def test_get_transaction_history(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):

    transaction_from = await factories.transaction(
        db_session,
        account.id,
        second_account.id,
        TransactionType.transfer,
        100,
        created=datetime.utcnow().replace(hour=0, minute=0),
    )
    transaction_to = await factories.transaction(
        db_session,
        second_account.id,
        account.id,
        TransactionType.transfer,
        200,
        created=datetime.utcnow().replace(hour=0, minute=1),
    )
    transaction_topup = await factories.transaction(
        db_session,
        settings.TOPUP_ACCOUNT_ID,
        account.id,
        TransactionType.topup,
        300,
        created=datetime.utcnow().replace(hour=0, minute=2),
    )
    transaction_to_second = await factories.transaction(
        db_session,
        settings.TOPUP_ACCOUNT_ID,
        second_account.id,
        TransactionType.topup,
        400,
        created=datetime.utcnow().replace(hour=0, minute=3),
    )

    response = await client.get("/transactions", auth=account.auth)
    assert response.status_code == 200, response.json()
    assert response.json() == [
        {
            "id": transaction_topup.id,
            "amount": 300,
            "type": "topup",
            "created": transaction_topup.created.isoformat(),
            "account_from": {
                "id": settings.TOPUP_ACCOUNT_ID,
                "username": "system:topup",
            },
            "account_to": {"id": account.id, "username": account.username},
        },
        {
            "id": transaction_to.id,
            "amount": 200,
            "type": "transfer",
            "created": transaction_to.created.isoformat(),
            "account_from": {
                "id": second_account.id,
                "username": second_account.username,
            },
            "account_to": {"id": account.id, "username": account.username},
        },
        {
            "id": transaction_from.id,
            "amount": 100,
            "type": "transfer",
            "created": transaction_from.created.isoformat(),
            "account_from": {"id": account.id, "username": account.username},
            "account_to": {
                "id": second_account.id,
                "username": second_account.username,
            },
        },
    ]


@pytest.mark.asyncio
async def test_get_transaction_history_from(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):

    transaction_early = await factories.transaction(
        db_session,
        account.id,
        second_account.id,
        TransactionType.transfer,
        100,
        created=datetime.now().replace(hour=0),
    )
    transaction_late = await factories.transaction(
        db_session,
        second_account.id,
        account.id,
        TransactionType.transfer,
        200,
        created=datetime.now().replace(hour=2),
    )

    response = await client.get(
        "/transactions",
        params={"dt_from": datetime.now().replace(hour=1), "order": "asc"},
        auth=account.auth,
    )
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["id"] == transaction_late.id


@pytest.mark.asyncio
async def test_get_transaction_history_to(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):

    transaction_early = await factories.transaction(
        db_session,
        account.id,
        second_account.id,
        TransactionType.transfer,
        100,
        created=datetime.now().replace(hour=0),
    )
    transaction_late = await factories.transaction(
        db_session,
        second_account.id,
        account.id,
        TransactionType.transfer,
        200,
        created=datetime.now().replace(hour=2),
    )

    response = await client.get(
        "/transactions",
        params={"dt_to": datetime.now().replace(hour=1)},
        auth=account.auth,
    )
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["id"] == transaction_early.id


@pytest.mark.asyncio
async def test_get_transaction_history_limit(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):

    transaction_early = await factories.transaction(
        db_session,
        account.id,
        second_account.id,
        TransactionType.transfer,
        100,
        created=datetime.now().replace(hour=0),
    )
    transaction_late = await factories.transaction(
        db_session,
        second_account.id,
        account.id,
        TransactionType.transfer,
        200,
        created=datetime.now().replace(hour=2),
    )

    response = await client.get(
        "/transactions", params={"limit": 1}, auth=account.auth
    )
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["id"] == transaction_late.id


@pytest.mark.asyncio
async def test_get_transaction_history_order_asc(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):

    transaction_early = await factories.transaction(
        db_session,
        account.id,
        second_account.id,
        TransactionType.transfer,
        100,
        created=datetime.now().replace(hour=0),
    )
    transaction_late = await factories.transaction(
        db_session,
        second_account.id,
        account.id,
        TransactionType.transfer,
        200,
        created=datetime.now().replace(hour=2),
    )

    response = await client.get(
        "/transactions", params={"order": "asc"}, auth=account.auth
    )
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json[0]["id"] == transaction_early.id
    assert response_json[1]["id"] == transaction_late.id


@pytest.mark.asyncio
async def test_get_transaction(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):
    transaction = await factories.transaction(
        db_session, account.id, second_account.id, TransactionType.transfer, 100
    )
    response = await client.get(
        f"/transactions/{transaction.id}",
        auth=account.auth,
    )
    assert response.status_code == 200, response.json()
    assert response.json() == {
        "id": transaction.id,
        "amount": 100,
        "type": "transfer",
        "created": transaction.created.isoformat(),
        "account_from": {"id": account.id, "username": account.username},
        "account_to": {
            "id": second_account.id,
            "username": second_account.username,
        },
    }


@pytest.mark.asyncio
async def test_cannot_get_another_account_transaction(
    account: Account,
    second_account: Account,
    client: httpx.AsyncClient,
    db_session: DB,
):

    transaction_to_second = await factories.transaction(
        db_session,
        settings.TOPUP_ACCOUNT_ID,
        second_account.id,
        TransactionType.topup,
        400,
    )
    response = await client.get(
        f"/transactions/{transaction_to_second.id}",
        auth=account.auth,
    )
    assert response.status_code == 404, response.json()


@pytest.mark.asyncio
async def test_cannot_get_unknown_transaction(
    account: Account, client: httpx.AsyncClient, db_session: DB
):

    response = await client.get(
        f"/transactions/unknown",
        auth=account.auth,
    )
    assert response.status_code == 404, response.json()
