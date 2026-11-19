
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.income import Income
from app.schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomeResponse
)

router = APIRouter(prefix="/api/income", tags=["Income"])


@router.post("/", response_model=IncomeResponse, status_code=201)
def create_income(
    data: IncomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income = Income(
        user_id=current_user.id,
        source=data.source,
        amount=data.amount,
        income_date=data.income_date,
        description=data.description
    )

    db.add(income)
    db.commit()
    db.refresh(income)

    return income


@router.get("/", response_model=list[IncomeResponse])
def get_income(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Income).filter(
        Income.user_id == current_user.id
    ).order_by(Income.income_date.desc()).all()


@router.put("/{income_id}", response_model=IncomeResponse)
def update_income(
    income_id: int,
    data: IncomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id
    ).first()

    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None or field == "description":
            setattr(income, field, value)

    db.commit()
    db.refresh(income)

    return income


@router.delete("/{income_id}")
def delete_income(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id
    ).first()

    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")

    db.delete(income)
    db.commit()

    return {"message": "Income deleted successfully"}
