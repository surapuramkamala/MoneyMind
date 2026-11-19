
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    total_income: Decimal
    total_expenses: Decimal
    investment_contributions: Decimal
    investment_sale_proceeds: Decimal
    cash_remaining: Decimal


class InvestmentValuationInput(BaseModel):
    investment_id: int
    current_unit_price: Decimal = Field(
        ge=0,
        max_digits=14,
        decimal_places=2
    )


class InvestmentProfitLossItem(BaseModel):
    investment_id: int
    investment_name: str
    quantity_held: Decimal
    invested_cost: Decimal
    current_market_value: Decimal
    realized_profit_loss: Decimal
    unrealized_profit_loss: Decimal


class PortfolioReportResponse(BaseModel):
    total_invested_cost: Decimal
    total_market_value: Decimal
    total_realized_profit_loss: Decimal
    total_unrealized_profit_loss: Decimal
    total_profit_loss: Decimal
    investments: list[InvestmentProfitLossItem]


class MonthlyTrendItem(BaseModel):
    month: int
    total_income: Decimal
    total_expenses: Decimal
    investment_contributions: Decimal
    cash_remaining: Decimal


class ExpenseCategoryItem(BaseModel):
    category: str
    total_amount: Decimal
    percentage: Decimal


class YearlyReportResponse(BaseModel):
    year: int
    total_income: Decimal
    total_expenses: Decimal
    investment_contributions: Decimal
    investment_sale_proceeds: Decimal
    cash_remaining: Decimal
    monthly_trends: list[MonthlyTrendItem]
    expense_categories: list[ExpenseCategoryItem]
    highest_spending_category: str | None


class DashboardSummaryResponse(BaseModel):
    year: int
    month: int
    total_income: Decimal
    total_expenses: Decimal
    investment_contributions: Decimal
    investment_sale_proceeds: Decimal
    cash_remaining: Decimal
    expense_categories: list[ExpenseCategoryItem]
    highest_spending_category: str | None

class YearlyMonthlySummary(BaseModel):
    month: int
    total_income: Decimal
    total_expenses: Decimal
    investment_contributions: Decimal
    investment_sale_proceeds: Decimal
    cash_remaining: Decimal


class YearlyReportResponse(BaseModel):
    year: int
    total_income: Decimal
    total_expenses: Decimal
    investment_contributions: Decimal
    investment_sale_proceeds: Decimal
    cash_remaining: Decimal
    monthly_summary: list[YearlyMonthlySummary]


class ExpenseCategoryItem(BaseModel):
    category: str
    total_amount: Decimal
    percentage: Decimal


class ExpenseBreakdownResponse(BaseModel):
    year: int
    month: int | None
    total_expenses: Decimal
    categories: list[ExpenseCategoryItem]