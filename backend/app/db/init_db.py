from sqlalchemy.orm import Session

from app import routes, pydanticModels
from app.core.config import settings
from app.db import base  # noqa
from app.db.session import SessionLocal


def init_db() -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables uncommenting the next line
    # Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    # Create first superuser if not exists
    user = routes.user.get_by_email(db, email="admin@example.com")
    if not user:
        user_in = pydanticModels.UserCreate(
            email="admin@example.com",
            password="admin123",
            is_superuser=True,
            full_name="Admin User"
        )
        user = routes.user.create(db, obj_in=user_in)
    
    db.close() 