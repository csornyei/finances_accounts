from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from uuid import UUID
from typing import TypedDict

from finances_accounts.logger import logger

from finances_shared.models import Account


class AccountSearchParams(TypedDict):
    name: str
    iban: str
    nickname: str
    all: bool = True


async def get_account(db: AsyncSession, account_id: UUID):
    result = await db.execute(
        select(Account)
        .where(Account.id == account_id)
        .options(selectinload(Account.aliases))
    )

    return result.scalar_one_or_none()


async def get_accounts(db: AsyncSession, search_params: AccountSearchParams):
    """
    Endpoint to get all accounts.
    """
    stmt = select(Account)

    if not search_params.get("all"):
        stmt = stmt.where(Account.parent_id.is_(None))

    if search_params.get("name"):
        stmt = stmt.where(Account.name.ilike(f"%{search_params['name']}%"))
    if search_params.get("iban"):
        stmt = stmt.where(Account.iban.ilike(f"%{search_params['iban']}%"))
    if search_params.get("nickname"):
        stmt = stmt.where(Account.nickname.ilike(f"%{search_params['nickname']}%"))

    result = await db.execute(stmt)

    return result.scalars().all()


async def create_account(db: AsyncSession, account: Account):
    try:
        db_account = Account(**account.model_dump())
        db.add(db_account)
        await db.commit()
        await db.refresh(db_account)
        return db_account
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"IntegrityError: {e.orig}")
        raise HTTPException(
            status_code=400,
            detail="Account with this name and IBAN or this nickname already exists.",
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


async def update_account(db: AsyncSession, account_id: UUID, account: Account):
    db_account = await get_account(db, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    for key, value in account.model_dump().items():
        setattr(db_account, key, value)
    await db.commit()
    await db.refresh(db_account)
    return db_account


async def delete_account(db: AsyncSession, account_id: UUID):
    db_account = await get_account(db, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    await db.delete(db_account)
    await db.commit()
    return {"ok": True}


async def add_alias(db: AsyncSession, account_id: UUID, alias_id: UUID):
    db_account = await get_account(db, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Parent account not found")
    alias_account = await get_account(db, alias_id)
    if alias_account is None:
        raise HTTPException(status_code=404, detail="Alias account not found")

    if db_account.id == alias_account.id:
        raise HTTPException(status_code=400, detail="Cannot add self as alias")

    if alias_account.parent_id is not None:
        raise HTTPException(
            status_code=400, detail="Alias account already has a parent"
        )

    if db_account.parent_id is not None:
        parent_id = db_account.parent_id
    else:
        parent_id = db_account.id

    alias_account.parent_id = parent_id
    await db.commit()
    await db.refresh(db_account)
    return alias_account
