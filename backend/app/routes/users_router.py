from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.pydanticModels import user as user_schema
from app.security import get_password_hash
from dependencies import get_db
import logging

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@router.post("/", response_model=user_schema.User)
def create_user_profile(
    *,
    db: Session = Depends(get_db),
    user_in: user_schema.UserCreate,
):
    # This is a simplified check. In a real application, you'd have a
    # dedicated service function like `get_user_by_email`.
    # For now, this check is commented out to keep it simple, but it is a good practice
    # existing_user = (
    #     db.query(models.user_profile.User)
    #     .filter(models.user_profile.User.email == user_in.email)
    #     .first()
    # )
    # if existing_user:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="The user with this email already exists in the system.",
    #     )
    user_data = user_in.model_dump(exclude={"financials", "password"})
    financials_data = user_in.financials.model_dump()

    hashed_password = get_password_hash(user_in.password)

    db_user = models.user_profile.User(**user_data, hashed_password=hashed_password)
    db_financials = models.user_financials_model.UserFinancials(
        **financials_data, user=db_user
    )

    db.add(db_user)
    db.add(db_financials)
    db.commit()
    db.refresh(db_user)

    return db_user 


@router.get("/{user_id}", response_model=user_schema.UserWithFinancials)
def get_user_profile(
    *,
    db: Session = Depends(get_db),
    user_id: int,
):
    """
    Retrieve the full profile for a specific user, including their financial data.
    """
    db_user = (
        db.query(models.user_profile.User)
        .filter(models.user_profile.User.id == user_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user
