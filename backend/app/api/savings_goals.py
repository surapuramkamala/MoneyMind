
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.savings_goal import SavingsGoal


router = APIRouter(
    prefix="/api/savings-goals",
    tags=["Savings Goals"],
)


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    target_amount: Decimal = Field(
        gt=0, max_digits=14, decimal_places=2
    )
    target_date: date | None = None


class SavingsGoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    target_amount: Decimal | None = Field(
        default=None, gt=0, max_digits=14, decimal_places=2
    )
    target_date: date | None = None


class SavingsContribution(BaseModel):
    amount: Decimal = Field(
        gt=0, max_digits=14, decimal_places=2
    )


def serialize_goal(goal):
    percentage = (
        goal.saved_amount / goal.target_amount
    ) * Decimal("100")

    remaining = max(
        Decimal("0"),
        goal.target_amount - goal.saved_amount,
    )

    return {
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "target_amount": goal.target_amount,
        "saved_amount": goal.saved_amount,
        "remaining_amount": remaining,
        "percentage_completed": round(percentage, 2),
        "is_completed": goal.saved_amount >= goal.target_amount,
        "target_date": goal.target_date,
        "created_at": goal.created_at,
    }


@router.post("/")
def create_goal(
    payload: SavingsGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    name = payload.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Goal name cannot be empty",
        )

    goal = SavingsGoal(
        user_id=current_user.id,
        name=name,
        description=payload.description,
        target_amount=payload.target_amount,
        saved_amount=Decimal("0"),
        target_date=payload.target_date,
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    return serialize_goal(goal)


@router.get("/")
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goals = (
        db.query(SavingsGoal)
        .filter(SavingsGoal.user_id == current_user.id)
        .order_by(SavingsGoal.created_at.desc())
        .all()
    )

    results = [serialize_goal(goal) for goal in goals]

    total_target = sum(
        (goal.target_amount for goal in goals),
        Decimal("0"),
    )

    total_saved = sum(
        (goal.saved_amount for goal in goals),
        Decimal("0"),
    )

    return {
        "total_goals": len(goals),
        "total_target": total_target,
        "total_saved": total_saved,
        "total_remaining": max(
            Decimal("0"), total_target - total_saved
        ),
        "goals": results,
    }


@router.put("/{goal_id}")
def update_goal(
    goal_id: int,
    payload: SavingsGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found",
        )

    changes = payload.model_dump(exclude_unset=True)

    for field, value in changes.items():
        if field == "name" and value is not None:
            value = value.strip()
            if not value:
                raise HTTPException(
                    status_code=400,
                    detail="Goal name cannot be empty",
                )

        if field == "target_amount" and value is not None:
            if value < goal.saved_amount:
                raise HTTPException(
                    status_code=400,
                    detail="Target amount cannot be lower than the amount already saved",
                )

        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)

    return serialize_goal(goal)


@router.post("/{goal_id}/contributions")
def add_contribution(
    goal_id: int,
    payload: SavingsContribution,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id,
    ).with_for_update().first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found",
        )

    goal.saved_amount += payload.amount

    db.commit()
    db.refresh(goal)

    return serialize_goal(goal)


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found",
        )

    db.delete(goal)
    db.commit()

    return {"message": "Savings goal deleted successfully"}
