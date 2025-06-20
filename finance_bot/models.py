# models.py
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from db import Base
import datetime

# 用户表（支持机器人多用户、多权限）
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(String, unique=True, index=True, nullable=False)  # Telegram 用户ID
    username = Column(String, index=True)
    is_admin = Column(Boolean, default=False)
    status = Column(String, default="active")  # active, banned, etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime)

    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("UserLog", back_populates="user", cascade="all, delete-orphan")

# 群组表（支持多群/分组管理）
class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    group_id = Column(String, unique=True, index=True, nullable=False)  # Telegram 群组ID
    group_name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    bills = relationship("Bill", back_populates="group", cascade="all, delete-orphan")

# 账单流水表（核心表）
class Bill(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="CNY")
    type = Column(String, default="income")  # income/expense/transfer
    rate = Column(Float, default=0)
    remark = Column(Text)
    status = Column(String, default="pending")  # pending/confirmed/canceled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confirmed_at = Column(DateTime)

    user = relationship("User", back_populates="bills")
    group = relationship("Group", back_populates="bills")

    __table_args__ = (
        Index('ix_bill_group_user', 'group_id', 'user_id'),
    )

# 钱包表（支持多链/多地址/标签）
class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    address = Column(String, unique=True, nullable=False)
    chain = Column(String, default="TRC20")
    tag = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="wallets")

# 汇率表（如需多币种/多链资产）
class ExchangeRate(Base):
    __tablename__ = 'exchange_rates'
    id = Column(Integer, primary_key=True)
    base = Column(String, nullable=False)
    target = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('base', 'target', name='_base_target_uc'),
    )

# 广告/通知表
class Announcement(Base):
    __tablename__ = 'announcements'
    id = Column(Integer, primary_key=True)
    group_id = Column(String, index=True)
    content = Column(Text, nullable=False)
    send_at = Column(DateTime, default=datetime.datetime.utcnow)
    sent = Column(Boolean, default=False)

# 操作日志表（用户行为审计/风控）
class UserLog(Base):
    __tablename__ = 'user_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String)
    detail = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="logs")

# 系统配置/全局键值对（可选）
class Config(Base):
    __tablename__ = 'config'
    key = Column(String, primary_key=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# 可继续扩展：权限表、分组规则、财务报表等
