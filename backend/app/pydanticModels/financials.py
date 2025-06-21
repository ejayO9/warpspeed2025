from datetime import datetime
from pydantic import BaseModel, Field


class MutualFundHolding(BaseModel):
    """
    Represents a summary of a single mutual fund holding.
    """

    isin: str = Field(..., description="International Securities Identification Number.")
    description: str = Field(..., description="Name or description of the mutual fund.")
    scheme_category: str = Field(..., description="Category of the scheme, e.g., LARGE_CAP_FUND.")
    scheme_option: str = Field(..., description="Option of the scheme, e.g., GROWTH, INCOME, BALANCED.")
    amc: str = Field(..., description="Asset Management Company.")
    units: float = Field(..., description="Total number of units held.")
    current_value: float = Field(..., description="Current market value of the holding.")
    cost_value: float = Field(..., description="The original cost of the investment.")
    nav: float = Field(..., description="Net Asset Value of the fund.")
    nav_date: datetime = Field(..., description="Date of the last NAV update.")


class EquityHolding(BaseModel):
    """
    Represents a summary of a single equity holding.
    """

    isin: str = Field(..., description="International Securities Identification Number.")
    description: str = Field(..., description="Description of the equity.")
    issuer_name: str = Field(..., description="Name of the company that issued the equity.")
    units: int = Field(..., description="Total number of units held.")
    current_value: float = Field(..., description="Current market value of the holding.")
    last_traded_price: float = Field(..., description="Last traded price per unit.")


class EtfHolding(BaseModel):
    """
    Represents a summary of a single ETF holding.
    """

    isin: str = Field(..., description="International Securities Identification Number.")
    description: str = Field(..., description="Description of the ETF.")
    units: float = Field(..., description="Total number of units held.")
    current_value: float = Field(..., description="Current market value of the holding.")
    nav: float = Field(..., description="Net Asset Value of the ETF.")
    last_nav_date: datetime = Field(..., description="Date of the last NAV update.")


class BalancePoint(BaseModel):
    """
    Represents a single data point in the user's balance history.
    """

    timestamp: datetime = Field(..., description="The timestamp of the balance record.")
    balance: float = Field(..., description="The account balance at the given timestamp.")


class TransactionPoint(BaseModel):
    """
    Represents a single transaction, for either inflow or outflow.
    """

    timestamp: datetime = Field(..., description="The timestamp of the transaction.")
    amount: float = Field(..., description="The amount of the transaction.")
    narration: str = Field(..., description="The transaction description or narration.")
    category: str = Field(..., description="The category assigned to the transaction.")
    balance: float = Field(..., description="The balance after the transaction.")
    type: str = Field(..., description="The type of the transaction. whether it is a credit or debit.")