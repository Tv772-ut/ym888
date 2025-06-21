from telegram import Update
from telegram.ext import ContextTypes

async def group_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 按群聚合统计
    await update.message.reply_text("本群已记账 30 笔，共计 5000 元（示例）")

async def group_settle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 群结算功能
    await update.message.reply_text("本群已结算，明细请查账单页面。")
