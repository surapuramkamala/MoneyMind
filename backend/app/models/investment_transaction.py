
from sqlalchemy import (
    Column, Integer, String, Numeric, Date,
    DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class InvestmentTransaction(Base):
    __tablename__ = "investment_transactions"

    id = Column(Integer, primary_key=True, index=True)

    investment_id = Column(
        Integer,
        ForeignKey("investments.id"),
        nullable=False
    )

    transaction_type = Column(String(20), nullable=False)
    quantity = Column(Numeric(18, 6), nullable=False)
    unit_price = Column(Numeric(14, 2), nullable=False)
    fees = Column(Numeric(14, 2), default=0, nullable=False)

    transaction_date = Column(Date, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    investment = relationship(
        "Investment",
        back_populates="transactions"
    )
