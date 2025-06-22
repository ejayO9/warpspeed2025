from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.user_financials_model import PydanticType
from app.pydanticModels.financial_analysis import FinancialAnalysis as FinancialAnalysisPydantic
from database import Base


class FinancialAnalysis(Base):
    __tablename__ = "financial_analysis"

    id = Column(Integer, primary_key=True, index=True)
    analysis = Column(PydanticType(pydantic_model=FinancialAnalysisPydantic), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="financial_analyses") 