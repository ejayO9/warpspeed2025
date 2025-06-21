from typing import Annotated, Any, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from database import SessionLocal
# from livekit.api import LiveKitAPI
from typing import AsyncGenerator
from contextlib import contextmanager



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]