# finance_bot/commands/help.py
from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/start - 启动机器人\n"
        "/help - 查看帮助\n"
        # ... 更多命令 ...
    )
    await update.message.reply_text(text)
