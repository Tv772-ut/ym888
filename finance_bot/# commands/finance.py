# commands/finance.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from models import Bill, User
from db import session
from sqlalchemy import func, extract
from sqlalchemy.exc import SQLAlchemyError
import datetime
import io
import pandas as pd

# ===== 1. 总览统计 =====
async def finance_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """财务总览：收入、支出、结余"""
    user_id = str(update.effective_user.id)
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                await update.message.reply_text("未找到用户信息。")
                return
            total_income = db.query(func.sum(Bill.amount)).filter(Bill.user_id==user.id, Bill.amount>0).scalar() or 0
            total_out = db.query(func.sum(Bill.amount)).filter(Bill.user_id==user.id, Bill.amount<0).scalar() or 0
            count = db.query(func.count(Bill.id)).filter(Bill.user_id==user.id).scalar()
            await update.message.reply_text(
                f"【财务总览】\n"
                f"总收入：{total_income:.2f}\n"
                f"总支出：{abs(total_out):.2f}\n"
                f"结余：{total_income + total_out:.2f}\n"
                f"共记账：{count} 笔"
            )
    except SQLAlchemyError as e:
        await update.message.reply_text(f"查询失败：{e}")

# ===== 2. 月度/年度账单汇总 =====
async def finance_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """本月账单汇总"""
    user_id = str(update.effective_user.id)
    now = datetime.datetime.utcnow()
    year = now.year
    month = now.month
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                await update.message.reply_text("未找到用户信息。")
                return
            bills = (
                db.query(Bill)
                .filter(Bill.user_id==user.id)
                .filter(extract('year', Bill.created_at) == year)
                .filter(extract('month', Bill.created_at) == month)
                .order_by(Bill.created_at.desc())
                .all()
            )
            income = sum(b.amount for b in bills if b.amount > 0)
            out = sum(b.amount for b in bills if b.amount < 0)
            msg = (
                f"【{year}年{month}月】\n"
                f"收入：{income:.2f}\n"
                f"支出：{abs(out):.2f}\n"
                f"结余：{income + out:.2f}\n"
                f"本月记账：{len(bills)} 笔"
            )
            await update.message.reply_text(msg)
    except SQLAlchemyError as e:
        await update.message.reply_text(f"查询失败：{e}")

async def finance_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """年度账单汇总"""
    user_id = str(update.effective_user.id)
    now = datetime.datetime.utcnow()
    year = now.year
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                await update.message.reply_text("未找到用户信息。")
                return
            bills = (
                db.query(Bill)
                .filter(Bill.user_id==user.id)
                .filter(extract('year', Bill.created_at) == year)
                .order_by(Bill.created_at.desc())
                .all()
            )
            income = sum(b.amount for b in bills if b.amount > 0)
            out = sum(b.amount for b in bills if b.amount < 0)
            msg = (
                f"【{year}年】\n"
                f"收入：{income:.2f}\n"
                f"支出：{abs(out):.2f}\n"
                f"结余：{income + out:.2f}\n"
                f"本年记账：{len(bills)} 笔"
            )
            await update.message.reply_text(msg)
    except SQLAlchemyError as e:
        await update.message.reply_text(f"查询失败：{e}")

# ===== 3. 导出Excel =====
async def export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """账单导出为Excel"""
    user_id = str(update.effective_user.id)
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                await update.message.reply_text("未找到用户信息。")
                return
            bills = db.query(Bill).filter_by(user_id=user.id).order_by(Bill.created_at.desc()).all()
            if not bills:
                await update.message.reply_text("暂无账单可导出。")
                return
            # 用 pandas 生成excel
            data = [
                {
                    "日期": b.created_at.strftime('%Y-%m-%d %H:%M'),
                    "金额": b.amount,
                    "币种": b.currency,
                    "备注": b.remark or "",
                }
                for b in bills
            ]
            df = pd.DataFrame(data)
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
        await update.message.reply_document(document=output, filename="账单明细.xlsx", caption="账单Excel已导出")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"导出失败：{e}")

# ===== 4. 预算提醒（示例：本月支出超预算自动提醒）=====
async def finance_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """本月预算提醒，用法：/预算 5000"""
    user_id = str(update.effective_user.id)
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("用法：/预算 金额（如：/预算 5000）")
        return
    budget = float(context.args[0])
    now = datetime.datetime.utcnow()
    year, month = now.year, now.month
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                await update.message.reply_text("未找到用户信息。")
                return
            out = (
                db.query(func.sum(Bill.amount))
                .filter(Bill.user_id==user.id)
                .filter(extract('year', Bill.created_at) == year)
                .filter(extract('month', Bill.created_at) == month)
                .filter(Bill.amount < 0)
                .scalar()
            ) or 0
            if abs(out) > budget:
                await update.message.reply_text(f"⚠️ 本月支出已超预算！\n预算：{budget:.2f}，支出：{abs(out):.2f}")
            else:
                await update.message.reply_text(f"本月预算：{budget:.2f}\n当前支出：{abs(out):.2f}\n尚未超支。")
    except SQLAlchemyError as e:
        await update.message.reply_text
