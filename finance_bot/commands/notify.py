from telegram import Update
from telegram.ext import ContextTypes
from finance_bot.config import settings
from finance_bot.utils import is_admin

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, settings.ADMIN_USER_IDS):
        await update.message.reply_text("🚫 你没有权限广播消息。")
        return
    if not context.args:
        await update.message.reply_text("请提供要广播的消息内容。")
        return

    message = " ".join(context.args)
    # 这里假设你有用户ID列表 user_ids
    user_ids = [123456789, 987654321]  # 示例，实际开发中应从数据库获取

    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            pass  # 可记录日志
    await update.message.reply_text("消息已广播。")
