import json
from typing import Any, List, Type, TypeVar
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON, TypeDecorator

from app.pydanticModels.financials import (
    BalancePoint,
    EquityHolding,
    EtfHolding,
    MutualFundHolding,
    TransactionPoint,
)
from database import Base

T = TypeVar("T", bound=BaseModel)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class PydanticType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def __init__(
        self, pydantic_model: Type[T], as_list: bool = False, *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self.pydantic_model = pydantic_model
        self.as_list = as_list

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        if value is None:
            return None

        if self.as_list:
            # Handle both Pydantic models and dictionaries
            result = []
            for item in value:
                if hasattr(item, 'model_dump'):
                    # It's a Pydantic model
                    result.append(item.model_dump(mode="json"))
                else:
                    # It's already a dictionary
                    result.append(item)
            return json.dumps(result, cls=DateTimeEncoder)
        else:
            # Single value
            if hasattr(value, 'model_dump'):
                # It's a Pydantic model
                return json.dumps(value.model_dump(mode="json"))
            else:
                # It's already a dictionary
                return json.dumps(value, cls=DateTimeEncoder)

    def process_result_value(self, value: Any, dialect: Any) -> List[T] | T | None:
        if value is None:
            return None

        data = json.loads(value)

        if self.as_list:
            return [self.pydantic_model.model_validate(item) for item in data]
        return self.pydantic_model.model_validate(data)


class UserFinancials(Base):
    __tablename__ = "user_financials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="financials")

    # Credit Report Data
    credit_score_name = Column(String, nullable=True)
    credit_score = Column(Integer, nullable=True)
    total_income = Column(Float, nullable=True)
    loans_balance = Column(Float, nullable=True)
    loans_sanctioned_amount = Column(Float, nullable=True)
    loans_past_due_amount = Column(Float, nullable=True)
    active_loans_count = Column(Integer, nullable=True)

    # Investment Summaries
    mutual_funds_summary = Column(
        PydanticType(MutualFundHolding, as_list=True), nullable=True
    )
    equities_summary = Column(PydanticType(EquityHolding, as_list=True), nullable=True)
    etf_summary = Column(PydanticType(EtfHolding, as_list=True), nullable=True)

    # Banking History
    bank_balance_history = Column(
        PydanticType(BalancePoint, as_list=True), nullable=True
    )
    inflow_history = Column(PydanticType(TransactionPoint, as_list=True), nullable=True)
    outflow_history = Column(
        PydanticType(TransactionPoint, as_list=True), nullable=True
    )
  

