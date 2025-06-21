# ym888/commands/account.py
from telegram import Update
from telegram.ext import ContextTypes
from models import AccountRecord
from db import get_db
from utils import parse_amount

async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("请提供金额和类别，例如：/account 99.9 餐饮")
        return
    amount = parse_amount(args[0])
    category = args[1] if len(args) > 1 else "未分类"
    note = " ".join(args[2:]) if len(args) > 2 else ""
    db = next(get_db())
    record = AccountRecord(user_id=update.effective_user.id, group_id=update.effective_chat.id,
                           amount=amount, category=category, note=note)
    db.add(record)
    db.commit()
    await update.message.reply_text(f"已记账：{amount} [{category}] {note}")
