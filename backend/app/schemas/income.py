
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class IncomeCreate(BaseModel):
    source: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    income_date: date
    description: str | None = Field(default=None, max_length=500)


class IncomeUpdate(BaseModel):
    source: str | None = Field(default=None, min_length=2, max_length=100)
    amount: Decimal | None = Field(
        default=None, gt=0, max_digits=14, decimal_places=2
    )
    income_date: date | None = None
    description: str | None = Field(default=None, max_length=500)


class IncomeResponse(BaseModel):
    id: int
    source: str
    amount: Decimal
    income_date: date
    description: str | None

    model_config = ConfigDict(from_attributes=True)
