import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum as SQLAlchemyEnum,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database import Base

if TYPE_CHECKING:
    from .user_financials_model import UserFinancials  # noqa: F401


class Gender(str, enum.Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Auth fields
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    # PII fields
    date_of_birth = Column(Date, nullable=True)
    gender = Column(SQLAlchemyEnum(Gender), nullable=True)
    pan_id = Column(String, unique=True, index=True, nullable=True)
    passport_id = Column(String, unique=True, index=True, nullable=True)
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    # Relationships
    financials = relationship(
        "UserFinancials",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    chat_info = relationship(
        "UserChatInfo",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    financial_analyses = relationship(
        "FinancialAnalysis",
        back_populates="user",
        cascade="all, delete-orphan",
    ) 