from telegram import Update
from telegram.ext import ContextTypes

async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 示例：/notify 群发通知
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("用法：/notify 通知内容")
        return
    # 实际项目这里应遍历群/用户进行群发，可接数据库
    await update.message.reply_text(f"通知已发送：{message}")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 欢迎新用户！")
