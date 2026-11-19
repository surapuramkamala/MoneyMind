
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.budget import Budget
from app.models.expense import Expense


router = APIRouter(
    prefix="/api/budgets",
    tags=["Monthly Budgets"]
)


# Request schema
class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)


class BudgetUpdate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


# Calculate category spending for a month
def get_monthly_spending(db, user_id, category, year, month):

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    total = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.user_id == user_id,
            Expense.category == category,
            Expense.expense_date >= start_date,
            Expense.expense_date < end_date
        )
        .scalar()
    )

    return Decimal(str(total))


# Format budget response
def serialize_budget(db, budget):

    spent = get_monthly_spending(
        db,
        budget.user_id,
        budget.category,
        budget.year,
        budget.month
    )

    remaining = budget.amount - spent
    percentage = (spent / budget.amount) * Decimal("100")

    if spent >= budget.amount:
        status = "exceeded"
    elif percentage >= Decimal("80"):
        status = "warning"
    else:
        status = "on_track"

    return {
        "id": budget.id,
        "category": budget.category,
        "budget_amount": budget.amount,
        "spent_amount": spent,
        "remaining_amount": remaining,
        "percentage_used": round(percentage, 2),
        "status": status,
        "year": budget.year,
        "month": budget.month
    }


# 1. CREATE BUDGET
@router.post("/")
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = payload.category.strip()

    if not category:
        raise HTTPException(
            status_code=400,
            detail="Category cannot be empty"
        )

    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == category,
        Budget.year == payload.year,
        Budget.month == payload.month
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Budget already exists for this category and month"
        )

    budget = Budget(
        user_id=current_user.id,
        category=category,
        amount=payload.amount,
        year=payload.year,
        month=payload.month
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return serialize_budget(db, budget)


# 2. GET MONTHLY BUDGETS
@router.get("/")
def get_budgets(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if month < 1 or month > 12:
        raise HTTPException(
            status_code=400,
            detail="Month must be between 1 and 12"
        )

    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.year == year,
        Budget.month == month
    ).order_by(Budget.category).all()

    results = [
        serialize_budget(db, item)
        for item in budgets
    ]

    total_budget = sum(
        (item["budget_amount"] for item in results),
        Decimal("0")
    )

    total_spent = sum(
        (item["spent_amount"] for item in results),
        Decimal("0")
    )

    return {
        "year": year,
        "month": month,
        "total_budget": total_budget,
        "total_spent": total_spent,
        "total_remaining": total_budget - total_spent,
        "budgets": results
    }


# 3. UPDATE BUDGET
@router.put("/{budget_id}")
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    budget.amount = payload.amount

    db.commit()
    db.refresh(budget)

    return serialize_budget(db, budget)


# 4. DELETE BUDGET
@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()

    return {
        "message": "Budget deleted successfully"
    }
