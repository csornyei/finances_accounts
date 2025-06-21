from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AccountBase(BaseModel):
    name: str
    iban: str
    nickname: str
    parent_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    pass


class AccountOut(AccountBase):
    id: UUID

    class Config:
        from_attributes = True


class AccountWithAliases(AccountOut):
    aliases: list[AccountOut] = []

    class Config:
        from_attributes = True


class AccountAlias(BaseModel):
    account_id: UUID
    alias_id: UUID

    class Config:
        from_attributes = True
