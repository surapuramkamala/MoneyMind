from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.advisor import AdvisorRequest, AdvisorResponse
from app.services.advisor_service import ask_financial_advisor

router = APIRouter(
    prefix="/api/advisor",
    tags=["AI Financial Advisor"]
)


@router.post("/ask", response_model=AdvisorResponse)
def ask_advisor(
    request: AdvisorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    answer = ask_financial_advisor(
        db=db,
        user_id=current_user.id,
        question=request.question,
        year=request.year,
        month=request.month
    )

    return {
        "answer": answer,
        "year": request.year,
        "month": request.month,
        "provider": "NVIDIA NIM"
    }