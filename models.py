# ym888/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class AccountRecord(Base):
    __tablename__ = "account_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    group_id = Column(Integer, index=True)
    amount = Column(Float)
    category = Column(String(50))
    note = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
