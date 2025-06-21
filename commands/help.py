from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = """
可用命令:
/start - 启动机器人
/help - 查看帮助
/account 金额 类别 备注 - 记账
/rate - 查询汇率
/group_summary - 群账单统计
/notify - 群发通知
/admin - 管理员功能
/wallet - 钱包功能
/watermark - 图片加水印
/ad - 广告推送
...
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)
