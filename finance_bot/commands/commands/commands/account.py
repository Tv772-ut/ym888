# finance_bot/commands/account.py
from telegram import Update
from telegram.ext import ContextTypes
from finance_bot.db import async_session
from finance_bot.models import AccountEntry
from finance_bot.utils import parse_amount

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with async_session() as session:
        amount = parse_amount(' '.join(context.args))
        entry = AccountEntry(user_id=update.effective_user.id, amount=amount, description=' '.join(context.args))
        session.add(entry)
        await session.commit()
        await update.message.reply_text(f"已记账：{amount} 元")
