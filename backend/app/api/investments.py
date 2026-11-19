
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.investment import Investment
from app.models.investment_transaction import InvestmentTransaction

from app.schemas.investment import (
    InvestmentCreate,
    InvestmentResponse,
    InvestmentTransactionCreate,
    InvestmentTransactionResponse,
    InvestmentHoldingResponse
)

router = APIRouter(prefix="/api/investments", tags=["Investments"])


@router.post("/", response_model=InvestmentResponse, status_code=201)
def create_investment(
    data: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investment = Investment(
        user_id=current_user.id,
        name=data.name,
        investment_type=data.investment_type,
        institution=data.institution,
        notes=data.notes
    )

    db.add(investment)
    db.commit()
    db.refresh(investment)

    return investment


@router.get("/", response_model=list[InvestmentResponse])
def get_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Investment).filter(
        Investment.user_id == current_user.id
    ).order_by(Investment.id.desc()).all()


@router.post(
    "/{investment_id}/transactions",
    response_model=InvestmentTransactionResponse,
    status_code=201
)
def add_investment_transaction(
    investment_id: int,
    data: InvestmentTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == current_user.id
    ).with_for_update().first()

    if not investment:
        raise HTTPException(
            status_code=404,
            detail="Investment not found"
        )

    transactions = db.query(InvestmentTransaction).filter(
        InvestmentTransaction.investment_id == investment_id
    ).all()

    quantity_held = Decimal("0")

    for transaction in transactions:
        if transaction.transaction_type == "BUY":
            quantity_held += transaction.quantity
        elif transaction.transaction_type == "SELL":
            quantity_held -= transaction.quantity

    if data.transaction_type == "SELL" and data.quantity > quantity_held:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient holdings. Available quantity: {quantity_held}"
        )

    transaction = InvestmentTransaction(
        investment_id=investment_id,
        transaction_type=data.transaction_type,
        quantity=data.quantity,
        unit_price=data.unit_price,
        fees=data.fees,
        transaction_date=data.transaction_date
    )

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save investment transaction"
        )


@router.get(
    "/{investment_id}/transactions",
    response_model=list[InvestmentTransactionResponse]
)
def get_investment_transactions(
    investment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == current_user.id
    ).first()

    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    return db.query(InvestmentTransaction).filter(
        InvestmentTransaction.investment_id == investment_id
    ).order_by(InvestmentTransaction.transaction_date.desc()).all()


@router.get(
    "/{investment_id}/holdings",
    response_model=InvestmentHoldingResponse
)
def get_investment_holdings(
    investment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == current_user.id
    ).first()

    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    transactions = db.query(InvestmentTransaction).filter(
        InvestmentTransaction.investment_id == investment_id
    ).all()

    quantity_held = Decimal("0")

    for transaction in transactions:
        if transaction.transaction_type == "BUY":
            quantity_held += transaction.quantity
        elif transaction.transaction_type == "SELL":
            quantity_held -= transaction.quantity

    return {
        "investment_id": investment.id,
        "investment_name": investment.name,
        "quantity_held": quantity_held
    }
