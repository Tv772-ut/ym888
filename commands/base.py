# ym888/commands/base.py
from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用 ym888 机器人！输入 /help 查看可用指令。")
