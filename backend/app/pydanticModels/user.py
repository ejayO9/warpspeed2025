from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from ..models.user_profile import Gender
from .financials import (
    BalancePoint,
    EquityHolding,
    EtfHolding,
    MutualFundHolding,
    TransactionPoint,
)


class UserFinancialsBase(BaseModel):
    credit_score_name: Optional[str] = None
    credit_score: Optional[int] = None
    total_income: Optional[float] = None
    loans_balance: Optional[float] = None
    loans_sanctioned_amount: Optional[float] = None
    loans_past_due_amount: Optional[float] = None
    active_loans_count: Optional[int] = None
    mutual_funds_summary: Optional[List[MutualFundHolding]] = []
    equities_summary: Optional[List[EquityHolding]] = []
    etf_summary: Optional[List[EtfHolding]] = []
    bank_balance_history: Optional[List[BalancePoint]] = []
    inflow_history: Optional[List[TransactionPoint]] = []
    outflow_history: Optional[List[TransactionPoint]] = []


class UserFinancialsCreate(UserFinancialsBase):
    pass


class UserFinancials(UserFinancialsBase):
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    pan_id: Optional[str] = None
    passport_id: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

    financials: UserFinancialsCreate


class User(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool

    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    pan_id: Optional[str] = None
    passport_id: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class UserWithFinancials(User):
    financials: Optional[UserFinancials] = None 