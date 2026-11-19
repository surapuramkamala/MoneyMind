
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


EXPENSE_CATEGORIES = [
    "Food",
    "Rent",
    "Shopping",
    "Travel",
    "Entertainment",
    "Healthcare",
    "Education",
    "Bills",
    "Groceries",
    "Transportation",
    "Other"
]


class ExpenseCreate(BaseModel):
    category: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    expense_date: date
    description: str | None = Field(default=None, max_length=500)


class ExpenseUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=2, max_length=100)
    amount: Decimal | None = Field(
        default=None, gt=0, max_digits=14, decimal_places=2
    )
    expense_date: date | None = None
    description: str | None = Field(default=None, max_length=500)


class ExpenseResponse(BaseModel):
    id: int
    category: str
    amount: Decimal
    expense_date: date
    description: str | None

    model_config = ConfigDict(from_attributes=True)
