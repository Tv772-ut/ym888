from telegram import Update
from telegram.ext import ContextTypes
from api.exchange_api import get_usdt_cny

async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rate = get_usdt_cny()
    if rate:
        await update.message.reply_text(f"最新 USDT/CNY 汇率：{rate}")
    else:
        await update.message.reply_text("汇率获取失败，请稍后再试。")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 示例：汇总账单（需接数据库实现）
    await update.message.reply_text("本群本月支出总计：¥12345.67（示例）")
