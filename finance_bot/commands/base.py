# finance_bot/commands/base.py
from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 欢迎使用高级记账机器人！\n输入 /help 查看功能。")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("暂不支持该输入，请输入 /help 查看可用命令。")
