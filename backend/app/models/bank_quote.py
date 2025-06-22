from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base

class BankQuote(Base):
    __tablename__ = "bank_quotes"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    tenure = Column(Integer, nullable=False) # Assuming tenure is in months
    interest_rate = Column(Float, nullable=False)
    emi = Column(Float, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User") 