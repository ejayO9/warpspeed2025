from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class UserChatInfo(Base):
    __tablename__ = "user_chat_info"

    id = Column(Integer, primary_key=True, index=True)
    income_details = Column(Text, nullable=True)
    upcoming_spends = Column(Text, nullable=True)
    dependents_info = Column(Text, nullable=True)
    additional_info = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="chat_info")
    