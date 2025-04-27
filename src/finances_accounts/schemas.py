from pydantic import BaseModel
from uuid import UUID
from typing import Optional


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
        orm_mode = True


class AccountAlias(BaseModel):
    account_id: UUID
    alias_id: UUID

    class Config:
        from_attributes = True
