from enum import Enum
from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field

class SplitType(str, Enum):
    EQUAL = "equal"
    PERCENTAGE = "percentage"
    EXACT = "exact"

class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserResponse(APIModel):
    id: UUID
    email: EmailStr
    full_name: str
    created_at: AwareDatetime
    updated_at: AwareDatetime


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GroupJoin(BaseModel):
    invite_code: str = Field(min_length=1, max_length=10)


class GroupResponse(APIModel):
    id: UUID
    name: str
    created_by: UUID
    invite_code: str
    created_at: AwareDatetime
    updated_at: AwareDatetime


class MemberResponse(APIModel):
    id: UUID
    group_id: UUID
    user_id: UUID
    joined_at: AwareDatetime


class ExpenseSplitCreate(BaseModel):
    user_id: UUID
    amount_owed: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    split_type: SplitType
    splits: list[ExpenseSplitCreate] = Field(min_length=1)


class ExpenseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    split_type: SplitType | None = None
    splits: list[ExpenseSplitCreate] | None = Field(default=None, min_length=1)


class ExpenseSplitResponse(APIModel):
    id: UUID
    expense_id: UUID
    user_id: UUID
    amount_owed: Decimal


class ExpenseResponse(APIModel):
    id: UUID
    group_id: UUID
    paid_by: UUID
    description: str
    amount: Decimal
    split_type: SplitType
    expense_date: date
    version: int
    created_at: AwareDatetime
    updated_at: AwareDatetime
    splits: list[ExpenseSplitResponse] = Field(default_factory=list)


class SettlementCreate(BaseModel):
    paid_to: UUID
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class SettlementResponse(APIModel):
    id: UUID
    group_id: UUID
    paid_by: UUID
    paid_to: UUID
    amount: Decimal
    settled_at: AwareDatetime


