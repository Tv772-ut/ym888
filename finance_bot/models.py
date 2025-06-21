from sqlalchemy import Integer, String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from finance_bot.db import Base

class AccountEntry(Base):
    __tablename__ = "account_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
