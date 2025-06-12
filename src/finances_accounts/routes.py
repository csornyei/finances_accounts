from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from finances_accounts import schemas, account_controller

from finances_shared.db import get_db

router = APIRouter()


@router.get("/accounts", response_model=list[schemas.AccountOut])
async def get_accounts(
    name: str = "",
    iban: str = "",
    nickname: str = "",
    all: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to get all accounts.
    """
    search_params = account_controller.AccountSearchParams(
        name=name, iban=iban, nickname=nickname, all=all
    )

    return await account_controller.get_accounts(db, search_params)


@router.post("/accounts", response_model=schemas.AccountOut)
async def create_account(
    account: schemas.AccountCreate, db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to create a new account.
    """
    try:
        if account.parent_id:
            parent_account = await account_controller.get_account(db, account.parent_id)
            if parent_account is None:
                raise HTTPException(status_code=404, detail="Parent account not found")

        account = await account_controller.create_account(db, account)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return account


@router.post("/accounts/alias")
async def create_alias(body: schemas.AccountAlias, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to add accound_id as an alias to the account id in the body.
    """
    try:
        account_id = body.account_id
        alias_id = body.alias_id

        return await account_controller.add_alias(db, account_id, alias_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_id}", response_model=schemas.AccountWithAliases)
async def get_account(account_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to get a specific account by ID.
    """
    account = await account_controller.get_account(db, account_id)

    print(account.__dict__)

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/accounts/{account_id}", response_model=schemas.AccountOut)
async def update_account(
    account: schemas.AccountUpdate, account_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to update a specific account by ID.
    """
    return await account_controller.update_account(db, account_id, account)


@router.delete("/accounts/{account_id}")
async def delete_account(account_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to delete a specific account by ID.
    """
    return await account_controller.delete_account(db, account_id)
