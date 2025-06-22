from pydantic import BaseModel
from typing import Optional


class UserChatInfoBase(BaseModel):
    income_details: Optional[str] = None
    upcoming_spends: Optional[str] = None
    dependents_info: Optional[str] = None
    additional_info: Optional[str] = None


class UserChatInfoCreate(UserChatInfoBase):
    pass


class UserChatInfo(UserChatInfoBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True 