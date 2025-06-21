# finance_bot/db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from finance_bot.config import settings

engine = create_async_engine(settings.DB_URL, echo=settings.DEBUG, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# 用于 Alembic 自动识别 Base
metadata = Base.metadata
