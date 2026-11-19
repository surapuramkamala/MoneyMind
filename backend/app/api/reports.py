from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.schemas.finance import (
    MonthlyReportResponse,
    InvestmentValuationInput,
    PortfolioReportResponse,
    YearlyReportResponse,
    DashboardSummaryResponse
)

from app.services.finance_service import (
    calculate_monthly_report,
    calculate_portfolio_report,
    calculate_yearly_report,
    calculate_dashboard_summary
)

from app.schemas.finance import (
    YearlyReportResponse,
    ExpenseBreakdownResponse
)

from app.services.finance_service import (
    calculate_yearly_report,
    calculate_expense_breakdown
)

router = APIRouter(
    prefix="/api/reports",
    tags=["Financial Reports"]
)


@router.get("/monthly", response_model=MonthlyReportResponse)
def monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return calculate_monthly_report(
        db=db,
        user_id=current_user.id,
        year=year,
        month=month
    )


@router.post(
    "/portfolio",
    response_model=PortfolioReportResponse
)
def portfolio_report(
    valuations: list[InvestmentValuationInput],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return calculate_portfolio_report(
        db=db,
        user_id=current_user.id,
        valuations=valuations
    )


@router.get("/yearly", response_model=YearlyReportResponse)
def yearly_report(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return calculate_yearly_report(
        db=db,
        user_id=current_user.id,
        year=year
    )


@router.get(
    "/dashboard",
    response_model=DashboardSummaryResponse
)
def dashboard_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return calculate_dashboard_summary(
        db=db,
        user_id=current_user.id,
        year=year,
        month=month
    )

@router.get("/yearly", response_model=YearlyReportResponse)
def yearly_report(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return calculate_yearly_report(
        db=db,
        user_id=current_user.id,
        year=year
    )


@router.get("/expense-breakdown", response_model=ExpenseBreakdownResponse)
def expense_breakdown(
    year: int,
    month: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return calculate_expense_breakdown(
        db=db,
        user_id=current_user.id,
        year=year,
        month=month
    )