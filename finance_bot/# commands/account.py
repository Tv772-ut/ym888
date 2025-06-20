# commands/account.py

import re
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from models import Bill, User
from db import session
from utils import parse_amount, safe_eval, format_amount
from sqlalchemy.exc import SQLAlchemyError

# 1. 记账命令
async def add_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/记账 100U|+88 记一笔账"""
    text = " ".join(context.args) if context.args else (update.message.text or "")
    amount, currency = parse_amount(text)
    if not amount:
        await update.message.reply_text("格式错误，请输入如：/记账 100U 或 /记账 +50")
        return

    user = get_or_create_user(update.effective_user)
    bill = Bill(user_id=user.id, amount=amount, currency=currency, remark=text)
    try:
        with session() as db:
            db.add(bill)
            db.commit()
        await update.message.reply_text(f"已记账：{format_amount(amount, currency)}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"记账失败：{e}")

# 2. 修正账单
async def fix_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/修正 账单ID 新金额[币种]  修改某一笔账单"""
    if len(context.args) < 2:
        await update.message.reply_text("用法：/修正 账单ID 新金额[币种]")
        return
    bill_id = context.args[0]
    new_amount, new_currency = parse_amount(context.args[1])
    try:
        with session() as db:
            bill = db.query(Bill).filter_by(id=bill_id).first()
            if not bill:
                await update.message.reply_text("账单不存在")
                return
            bill.amount = new_amount
            bill.currency = new_currency
            db.commit()
        await update.message.reply_text("账单已修正")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"修正失败：{e}")

# 3. 智能计算器
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/计算 1+2*3  或者直接发送公式"""
    expr = " ".join(context.args) if context.args else (update.message.text or "")
    expr = re.sub(r'^/计算\s*', '', expr)
    try:
        result = safe_eval(expr)
        await update.message.reply_text(f"{expr.strip()} = {result}")
    except Exception as e:
        await update.message.reply_text(f"计算失败：{e}")

# 4. 查询最近账单
async def recent_bills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/最近账单 查询10条"""
    user = get_or_create_user(update.effective_user)
    try:
        with session() as db:
            bills = (
                db.query(Bill)
                .filter_by(user_id=user.id)
                .order_by(Bill.created_at.desc())
                .limit(10)
                .all()
            )
            if not bills:
                await update.message.reply_text("暂无记录")
                return
            msg = "\n".join(
                [f"{b.id}: {format_amount(b.amount, b.currency)} {b.created_at:%m-%d %H:%M}" for b in bills]
            )
            await update.message.reply_text(f"最近账单：\n{msg}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"查询失败：{e}")

# 5. 直接解析纯金额消息（如+88、-50U），自动记账
async def auto_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """监听纯金额消息自动记账"""
    text = update.message.text.strip()
    if re.match(r'^[+-]?\d+(\.\d+)?[a-zA-Z]*$', text):
        amount, currency = parse_amount(text)
        if amount:
            user = get_or_create_user(update.effective_user)
            bill = Bill(user_id=user.id, amount=amount, currency=currency, remark=text)
            try:
                with session() as db:
                    db.add(bill)
                    db.commit()
                await update.message.reply_text(f"自动记账：{format_amount(amount, currency)}")
            except SQLAlchemyError as e:
                await update.message.reply_text(f"自动记账失败：{e}")

# 工具函数：获取或创建用户
def get_or_create_user(telegram_user):
    with session() as db:
        user = db.query(User).filter_by(tg_id=str(telegram_user.id)).first()
        if not user:
            user = User(tg_id=str(telegram_user.id), username=telegram_user.username or "")
            db.add(user)
            db.commit()
        return user

# 注册本模块所有命令
def register(app):
    app.add_handler(CommandHandler("记账", add_bill))
    app.add_handler(CommandHandler("fix", fix_bill))
    app.add_handler(CommandHandler("修正", fix_bill))
    app.add_handler(CommandHandler("计算", calc))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("最近账单", recent_bills))
    # 监听纯金额消息
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto_record))
