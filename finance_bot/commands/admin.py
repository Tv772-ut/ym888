from telegram import Update
from telegram.ext import ContextTypes
from finance_bot.config import settings
from finance_bot.utils import is_admin

async def admin_only_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, settings.ADMIN_USER_IDS):
        await update.message.reply_text("🚫 你没有管理员权限。")
        return
    await update.message.reply_text("这是管理员专用命令。")
