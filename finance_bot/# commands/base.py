# commands/base.py

from telegram import Update
from telegram.ext import ContextTypes
from config import ADMINS

# 通用权限检查装饰器
def admin_required(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if str(user_id) not in ADMINS:
            await update.message.reply_text("权限不足，仅管理员可执行此操作。")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# 通用错误处理
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        raise context.error
    except Exception as e:
        if hasattr(update, "message"):
            await update.message.reply_text(f"发生错误: {e}")
        # 可以扩展日志功能

# /start 命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "欢迎使用 ym888 记账机器人！输入 /help 查看所有命令。"
    )

# /help 命令
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "【常用命令说明】\n"
        "/记账 <金额>[币种] - 添加账单。如 /记账 100U\n"
        "/统计 - 查看账单统计\n"
        "/转账 <金额> @用户 - 群组内转账\n"
        "/导出 - 导出账单Excel\n"
        "/设置 - 个人或群组设置\n"
        "/帮助 - 查看本帮助\n"
    )
    await update.message.reply_text(msg)

# 基础命令注册
def register(app):
    from telegram.ext import CommandHandler

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    # 你也可以在这里添加更多基础命令

    # 全局错误处理（建议主入口也注册一次）
    app.add_error_handler(error_handler)
