from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.pydanticModels import user as user_schema
from app.pydanticModels import financials as financials_schema
from app.pydanticModels import user_chat_info as user_chat_info_schema
from app.pydanticModels import financial_analysis as financial_analysis_schema
from app.security import get_password_hash
from dependencies import get_db
import logging
from typing import List

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


@router.post("/{user_id}/bank-quotes", response_model=financials_schema.BankQuote)
def create_bank_quote(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    bank_quote_in: financials_schema.BankQuoteCreate,
):
    """
    Create a new bank quote for a specific user.
    """
    # Check if user exists
    db_user = (
        db.query(models.user_profile.User)
        .filter(models.user_profile.User.id == user_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create bank quote
    bank_quote_data = bank_quote_in.model_dump()
    db_bank_quote = models.bank_quote.BankQuote(
        **bank_quote_data, user_id=user_id
    )

    db.add(db_bank_quote)
    db.commit()
    db.refresh(db_bank_quote)

    return db_bank_quote


@router.get("/{user_id}/bank-quotes", response_model=List[financials_schema.BankQuote])
def get_user_bank_quotes(
    *,
    db: Session = Depends(get_db),
    user_id: int,
):
    """
    Retrieve all bank quotes for a specific user.
    """
    # Check if user exists
    db_user = (
        db.query(models.user_profile.User)
        .filter(models.user_profile.User.id == user_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all bank quotes for the user
    bank_quotes = (
        db.query(models.bank_quote.BankQuote)
        .filter(models.bank_quote.BankQuote.user_id == user_id)
        .all()
    )

    return bank_quotes


@router.post("/{user_id}/chat-info", response_model=user_chat_info_schema.UserChatInfo)
def create_user_chat_info(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    chat_info_in: user_chat_info_schema.UserChatInfoCreate,
):
    """
    Create new chat info for a specific user.
    """
    db_user = (
        db.query(models.user_profile.User)
        .filter(models.user_profile.User.id == user_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    chat_info_data = chat_info_in.model_dump()
    db_chat_info = models.user_chat_info_model.UserChatInfo(
        **chat_info_data, user_id=user_id
    )

    db.add(db_chat_info)
    db.commit()
    db.refresh(db_chat_info)

    return db_chat_info


@router.post("/{user_id}/financial-analysis", response_model=financial_analysis_schema.FinancialAnalysis)
def create_financial_analysis(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    financial_analysis_in: financial_analysis_schema.FinancialAnalysisCreate,
):
    """
    Create new financial analysis for a specific user.
    """
    db_user = (
        db.query(models.user_profile.User)
        .filter(models.user_profile.User.id == user_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    analysis_data = financial_analysis_in
    db_financial_analysis = models.financial_analysis.FinancialAnalysis(
        analysis=analysis_data, user_id=user_id
    )

    db.add(db_financial_analysis)
    db.commit()
    db.refresh(db_financial_analysis)
    
    # We need to return a pydantic model, not a db model with a pydantic model inside
    return db_financial_analysis.analysis


@router.get("/{user_id}/chat-info", response_model=List[user_chat_info_schema.UserChatInfo])
def get_user_chat_info(
    *,
    db: Session = Depends(get_db),
    user_id: int,
):
    """
    Retrieve all chat info records for a specific user.
    """
    # Check if user exists
    db_user = (
        db.query(models.user_profile.User)
        .filter(models.user_profile.User.id == user_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all chat info for the user
    chat_infos = (
        db.query(models.user_chat_info_model.UserChatInfo)
        .filter(models.user_chat_info_model.UserChatInfo.user_id == user_id)
        .all()
    )

    return chat_infos


@router.get("/{user_id}/financial-analyses", response_model=List[financial_analysis_schema.FinancialAnalysis])
def get_user_financial_analyses(
    *,
    db: Session = Depends(get_db),
    user_id: int,
):
    """
    Retrieve all financial analyses for a specific user.
    """
    # Check if user exists
    db_user = (
        db.query(models.user_profile.User)
        .filter(models.user_profile.User.id == user_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all financial analyses for the user
    analyses = (
        db.query(models.financial_analysis.FinancialAnalysis)
        .filter(models.financial_analysis.FinancialAnalysis.user_id == user_id)
        .all()
    )

    # Extract the Pydantic models from the database models
    return [analysis.analysis for analysis in analyses]
