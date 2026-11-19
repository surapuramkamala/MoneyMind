
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.income import Income
from app.models.expense import Expense
from app.models.investment import Investment
from app.models.investment_transaction import InvestmentTransaction


ZERO = Decimal("0")


def get_month_range(year: int, month: int):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be 1-12")

    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Invalid year")

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    return start_date, end_date


def calculate_monthly_report(
    db: Session,
    user_id: int,
    year: int,
    month: int
):
    start_date, end_date = get_month_range(year, month)

    incomes = db.query(Income).filter(
        Income.user_id == user_id,
        Income.income_date >= start_date,
        Income.income_date < end_date
    ).all()

    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.expense_date >= start_date,
        Expense.expense_date < end_date
    ).all()

    total_income = sum(
        (item.amount for item in incomes), ZERO
    )

    total_expenses = sum(
        (item.amount for item in expenses), ZERO
    )

    transactions = (
        db.query(InvestmentTransaction)
        .join(Investment)
        .filter(
            Investment.user_id == user_id,
            InvestmentTransaction.transaction_date >= start_date,
            InvestmentTransaction.transaction_date < end_date
        )
        .all()
    )

    investment_contributions = ZERO
    investment_sale_proceeds = ZERO

    for transaction in transactions:
        if transaction.transaction_type == "BUY":
            investment_contributions += (
                transaction.quantity * transaction.unit_price
                + transaction.fees
            )

        elif transaction.transaction_type == "SELL":
            investment_sale_proceeds += (
                transaction.quantity * transaction.unit_price
                - transaction.fees
            )

    cash_remaining = (
        total_income
        - total_expenses
        - investment_contributions
        + investment_sale_proceeds
    )

    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "investment_contributions": investment_contributions,
        "investment_sale_proceeds": investment_sale_proceeds,
        "cash_remaining": cash_remaining
    }


def calculate_investment_position(
    db: Session,
    user_id: int,
    investment_id: int,
    current_unit_price: Decimal
):
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == user_id
    ).first()

    if not investment:
        raise HTTPException(
            status_code=404,
            detail="Investment not found"
        )

    transactions = db.query(InvestmentTransaction).filter(
        InvestmentTransaction.investment_id == investment_id
    ).order_by(
        InvestmentTransaction.transaction_date,
        InvestmentTransaction.id
    ).all()

    quantity_held = ZERO
    invested_cost = ZERO
    realized_profit_loss = ZERO

    for transaction in transactions:
        quantity = transaction.quantity
        fees = transaction.fees

        if transaction.transaction_type == "BUY":
            buy_cost = quantity * transaction.unit_price + fees
            quantity_held += quantity
            invested_cost += buy_cost

        elif transaction.transaction_type == "SELL":
            if quantity > quantity_held:
                raise HTTPException(
                    status_code=400,
                    detail="Historical sale exceeds available holdings"
                )

            average_cost = invested_cost / quantity_held

            net_sale_proceeds = (
                quantity * transaction.unit_price - fees
            )

            cost_of_units_sold = average_cost * quantity

            realized_profit_loss += (
                net_sale_proceeds - cost_of_units_sold
            )

            quantity_held -= quantity
            invested_cost -= cost_of_units_sold

    if quantity_held == ZERO:
        invested_cost = ZERO

    current_market_value = quantity_held * current_unit_price

    unrealized_profit_loss = (
        current_market_value - invested_cost
    )

    return {
        "investment_id": investment.id,
        "investment_name": investment.name,
        "quantity_held": quantity_held,
        "invested_cost": invested_cost,
        "current_market_value": current_market_value,
        "realized_profit_loss": realized_profit_loss,
        "unrealized_profit_loss": unrealized_profit_loss
    }


def calculate_portfolio_report(
    db: Session,
    user_id: int,
    valuations: list
):
    investments = db.query(Investment).filter(
        Investment.user_id == user_id
    ).all()

    valuation_map = {
        item.investment_id: item.current_unit_price
        for item in valuations
    }

    results = []

    for investment in investments:
        if investment.id not in valuation_map:
            raise HTTPException(
                status_code=400,
                detail=f"Missing current price for {investment.name}"
            )

        result = calculate_investment_position(
            db,
            user_id,
            investment.id,
            valuation_map[investment.id]
        )

        results.append(result)

    total_cost = sum(
        (item["invested_cost"] for item in results), ZERO
    )
    total_market_value = sum(
        (item["current_market_value"] for item in results), ZERO
    )
    total_realized = sum(
        (item["realized_profit_loss"] for item in results), ZERO
    )
    total_unrealized = sum(
        (item["unrealized_profit_loss"] for item in results), ZERO
    )

    return {
        "total_invested_cost": total_cost,
        "total_market_value": total_market_value,
        "total_realized_profit_loss": total_realized,
        "total_unrealized_profit_loss": total_unrealized,
        "total_profit_loss": total_realized + total_unrealized,
        "investments": results
    }


def calculate_expense_breakdown(
    db, user_id, start_date, end_date
):
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.expense_date >= start_date,
        Expense.expense_date < end_date
    ).all()

    category_totals = {}

    for expense in expenses:
        category = expense.category
        category_totals[category] = (
            category_totals.get(category, ZERO) + expense.amount
        )

    total_expenses = sum(category_totals.values(), ZERO)

    results = []

    for category, amount in sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        percentage = ZERO

        if total_expenses > ZERO:
            percentage = (
                amount / total_expenses * Decimal("100")
            )

        results.append({
            "category": category,
            "total_amount": amount,
            "percentage": percentage.quantize(Decimal("0.01"))
        })

    return results


def calculate_yearly_report(db, user_id, year):
    if year < 2000 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Invalid year"
        )

    monthly_trends = []

    total_income = ZERO
    total_expenses = ZERO
    total_investment_contributions = ZERO
    total_investment_sale_proceeds = ZERO
    total_cash_remaining = ZERO

    for month in range(1, 13):
        report = calculate_monthly_report(
            db=db,
            user_id=user_id,
            year=year,
            month=month
        )

        monthly_trends.append({
            "month": month,
            "total_income": report["total_income"],
            "total_expenses": report["total_expenses"],
            "investment_contributions": report[
                "investment_contributions"
            ],
            "cash_remaining": report["cash_remaining"]
        })

        total_income += report["total_income"]
        total_expenses += report["total_expenses"]
        total_investment_contributions += report[
            "investment_contributions"
        ]
        total_investment_sale_proceeds += report[
            "investment_sale_proceeds"
        ]
        total_cash_remaining += report["cash_remaining"]

    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)

    expense_categories = calculate_expense_breakdown(
        db, user_id, start_date, end_date
    )

    highest_category = (
        expense_categories[0]["category"]
        if expense_categories else None
    )

    return {
        "year": year,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "investment_contributions": total_investment_contributions,
        "investment_sale_proceeds": total_investment_sale_proceeds,
        "cash_remaining": total_cash_remaining,
        "monthly_trends": monthly_trends,
        "expense_categories": expense_categories,
        "highest_spending_category": highest_category
    }


def calculate_dashboard_summary(db, user_id, year, month):
    monthly_report = calculate_monthly_report(
        db=db,
        user_id=user_id,
        year=year,
        month=month
    )

    start_date, end_date = get_month_range(year, month)

    expense_categories = calculate_expense_breakdown(
        db, user_id, start_date, end_date
    )

    highest_category = (
        expense_categories[0]["category"]
        if expense_categories else None
    )

    return {
        **monthly_report,
        "expense_categories": expense_categories,
        "highest_spending_category": highest_category
    }

def calculate_yearly_report(db, user_id, year):
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Invalid year")

    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)

    incomes = db.query(Income).filter(
        Income.user_id == user_id,
        Income.income_date >= start_date,
        Income.income_date < end_date
    ).all()

    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.expense_date >= start_date,
        Expense.expense_date < end_date
    ).all()

    transactions = (
        db.query(InvestmentTransaction)
        .join(Investment)
        .filter(
            Investment.user_id == user_id,
            InvestmentTransaction.transaction_date >= start_date,
            InvestmentTransaction.transaction_date < end_date
        )
        .all()
    )

    monthly_data = {}

    for month in range(1, 13):
        monthly_data[month] = {
            "total_income": ZERO,
            "total_expenses": ZERO,
            "investment_contributions": ZERO,
            "investment_sale_proceeds": ZERO,
        }

    for item in incomes:
        monthly_data[item.income_date.month]["total_income"] += item.amount

    for item in expenses:
        monthly_data[item.expense_date.month]["total_expenses"] += item.amount

    for transaction in transactions:
        month_data = monthly_data[transaction.transaction_date.month]

        if transaction.transaction_type == "BUY":
            month_data["investment_contributions"] += (
                transaction.quantity * transaction.unit_price
                + transaction.fees
            )

        elif transaction.transaction_type == "SELL":
            month_data["investment_sale_proceeds"] += (
                transaction.quantity * transaction.unit_price
                - transaction.fees
            )

    monthly_summary = []

    total_income = ZERO
    total_expenses = ZERO
    total_contributions = ZERO
    total_sale_proceeds = ZERO

    for month in range(1, 13):
        item = monthly_data[month]

        cash_remaining = (
            item["total_income"]
            - item["total_expenses"]
            - item["investment_contributions"]
            + item["investment_sale_proceeds"]
        )

        monthly_summary.append({
            "month": month,
            **item,
            "cash_remaining": cash_remaining
        })

        total_income += item["total_income"]
        total_expenses += item["total_expenses"]
        total_contributions += item["investment_contributions"]
        total_sale_proceeds += item["investment_sale_proceeds"]

    return {
        "year": year,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "investment_contributions": total_contributions,
        "investment_sale_proceeds": total_sale_proceeds,
        "cash_remaining": (
            total_income
            - total_expenses
            - total_contributions
            + total_sale_proceeds
        ),
        "monthly_summary": monthly_summary
    }


def calculate_expense_breakdown(db, user_id, year, month=None):
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Invalid year")

    if month is not None and (month < 1 or month > 12):
        raise HTTPException(status_code=400, detail="Month must be 1-12")

    query = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.expense_date >= date(year, 1, 1),
        Expense.expense_date < date(year + 1, 1, 1)
    )

    if month is not None:
        start_date, end_date = get_month_range(year, month)
        query = query.filter(
            Expense.expense_date >= start_date,
            Expense.expense_date < end_date
        )

    expenses = query.all()

    category_totals = {}

    for expense in expenses:
        category_totals[expense.category] = (
            category_totals.get(expense.category, ZERO) + expense.amount
        )

    total_expenses = sum(category_totals.values(), ZERO)

    categories = []

    for category, amount in sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        percentage = (
            (amount / total_expenses) * Decimal("100")
            if total_expenses > ZERO
            else ZERO
        )

        categories.append({
            "category": category,
            "total_amount": amount,
            "percentage": percentage.quantize(Decimal("0.01"))
        })

    return {
        "year": year,
        "month": month,
        "total_expenses": total_expenses,
        "categories": categories
    }