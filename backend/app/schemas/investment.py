
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class InvestmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    investment_type: Literal[
        "Stocks",
        "Mutual Funds",
        "SIP",
        "Gold",
        "Fixed Deposit",
        "Business",
        "Other"
    ]
    institution: str | None = Field(default=None, max_length=150)
    notes: str | None = Field(default=None, max_length=500)


class InvestmentResponse(BaseModel):
    id: int
    name: str
    investment_type: str
    institution: str | None
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


class InvestmentTransactionCreate(BaseModel):
    transaction_type: Literal["BUY", "SELL"]
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=6)
    unit_price: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    fees: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    transaction_date: date


class InvestmentTransactionResponse(BaseModel):
    id: int
    investment_id: int
    transaction_type: str
    quantity: Decimal
    unit_price: Decimal
    fees: Decimal
    transaction_date: date

    model_config = ConfigDict(from_attributes=True)


class InvestmentHoldingResponse(BaseModel):
    investment_id: int
    investment_name: str
    quantity_held: Decimal
