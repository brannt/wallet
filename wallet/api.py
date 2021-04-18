"""
API definitions
"""
from typing import List, Optional

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import conint

from .auth import get_password_hash
from .db import DB
from .deps import db, get_current_user
from .models import (
    Account,
    AccountCreate,
    AccountResponse,
    Ordering,
    Transaction,
    TransactionCreate,
    TransactionType,
)
from .settings import settings

router = APIRouter()


@router.get("/account", response_model=AccountResponse)
async def get_account(user: Account = Depends(get_current_user)) -> Account:
    """
    Get account info for the authenticated account
    """
    return user


@router.post(
    "/account",
    status_code=status.HTTP_201_CREATED,
    response_model=AccountResponse,
)
async def create_account(body: AccountCreate, db: DB = Depends(db)) -> Account:
    """
    Create a new account
    """
    try:
        await db.create_account(
            username=body.username,
            password=get_password_hash(body.password.get_secret_value()),
        )
        return await db.get_account(body.username)
    except db.dbapi.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "User already exists"},
        )


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    db: DB = Depends(db),
    user: Account = Depends(get_current_user),
    dt_from: Optional[datetime] = None,
    dt_to: Optional[datetime] = None,
    limit: Optional[conint(le=1000)] = 100,
    order: Optional[Ordering] = Ordering.desc,
) -> list[Transaction]:
    """
    Get transaction history of the authenticated account
    """
    if dt_from is None and dt_to is None:
        dt_to = datetime.utcnow().replace(microsecond=0)
        dt_from = dt_to.replace(hour=0, minute=0, second=0)
    error = None
    if dt_from is not None and dt_to is not None and dt_from > dt_to:
        error = "dt_from must be earlier than dt_to"
    elif order is Ordering.desc and dt_to is None:
        error = "Specify dt_to with descending order"
    elif order is Ordering.asc and dt_from is None:
        error = "Specify dt_from with ascending order"
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": error},
        )

    return await db.get_transactions(user.id, dt_from, dt_to, limit, order)


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(
    db: DB = Depends(db),
    user: Account = Depends(get_current_user),
    transaction_id: str = Query(..., alias="transactionId"),
) -> Transaction:
    """
    Get transaction by ID
    """
    transaction = await db.get_transaction(transaction_id, user.id)
    if transaction is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return transaction


@router.put(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
async def create_transaction(
    body: TransactionCreate,
    db: DB = Depends(db),
    user: Account = Depends(get_current_user),
    transaction_id: str = Query(..., alias="transactionId"),
) -> None:
    """
    Create a transaction.

    Clients should generate a random `transactionId` and pass it again if they have to retry the transaction.
    """
    if body.type is TransactionType.transfer:
        account_from_id = user.id
        account_to = await db.get_account(
            body.account_to.id
            if body.account_to.id is not None
            else body.account_to.username
        )

        if account_to is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": "Unknown account"},
            )

        account_to_id = account_to.id
        if account_to_id == settings.TOPUP_ACCOUNT_ID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": "Cannot transfer to system account"},
            )

    else:
        account_from_id = settings.TOPUP_ACCOUNT_ID
        account_to_id = user.id

    try:
        await db.create_transaction(
            transaction_id,
            account_from=account_from_id,
            account_to=account_to_id,
            amount=body.amount,
            type_=body.type,
        )
    except (db.dbapi.IntegrityError, db.dbapi.InternalError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
        )

    return "OK"
