# commands/ad.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ADMINS
from models import Ad, Group
from db import session
from sqlalchemy.exc import SQLAlchemyError
import datetime

# ===== 权限检查装饰器（仅管理员可发广告） =====
def admin_required(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in ADMINS:
            await update.message.reply_text("⚠️ 仅管理员可操作广告推送命令。")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ===== 1. 广告推送命令 =====
@admin_required
async def push_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /推送广告 广告内容
    """
    if not context.args:
        await update.message.reply_text("用法：/推送广告 <广告内容>")
        return
    content = " ".join(context.args)
    group_id = str(update.effective_chat.id)
    now = datetime.datetime.utcnow()
    try:
        with session() as db:
            # 可扩展按 group_id 控制广告投放
            ad = Ad(group_id=group_id, content=content, sent_at=now)
            db.add(ad)
            db.commit()
        await update.message.reply_text("✅ 广告已推送！")
        # 广播广告到群
        await context.bot.send_message(chat_id=group_id, text=f"📢 广告：{content}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"广告推送失败：{e}")

# ===== 2. 定时批量广告推送（可配合调度器定时调用）=====
async def push_pending_ads(context: ContextTypes.DEFAULT_TYPE):
    """
    定时发送未推送广告，需配合 APScheduler/Celery 调用
    """
    try:
        with session() as db:
            ads = db.query(Ad).filter_by(sent=False).all()
            for ad in ads:
                await context.bot.send_message(chat_id=ad.group_id, text=f"📢 广告：{ad.content}")
                ad.sent = True
                ad.sent_at = datetime.datetime.utcnow()
            db.commit()
    except SQLAlchemyError as e:
        print(f"[定时广告推送失败] {e}")

# ===== 3. 广告历史查询（管理员可查最近N条）=====
@admin_required
async def ad_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /广告历史 [数量]
    """
    group_id = str(update.effective_chat.id)
    limit = int(context.args[0]) if context.args and context.args[0].isdigit() else 5
    try:
        with session() as db:
            ads = (
                db.query(Ad)
                .filter_by(group_id=group_id)
                .order_by(Ad.sent_at.desc())
                .limit(limit)
                .all()
            )
            if not ads:
                await update.message.reply_text("暂无广告历史。")
                return
            msg = "\n\n".join([f"{ad.sent_at:%Y-%m-%d %H:%M}\n{ad.content}" for ad in ads])
            await update.message.reply_text("最近广告：\n" + msg)
    except SQLAlchemyError as e:
        await update.message.reply_text(f"查询失败：{e}")

# ===== 4. 删除历史广告（如需，管理员）=====
@admin_required
async def delete_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /删除广告 <广告ID>
    """
    if not context.args:
        await update.message.reply_text("用法：/删除广告 <广告ID>")
        return
    ad_id = context.args[0]
    try:
        with session() as db:
            ad = db.query(Ad).filter_by(id=ad_id).first()
            if not ad:
                await update.message.reply_text("未找到该广告。")
                return
            db.delete(ad)
            db.commit()
        await update.message.reply_text(f"广告 {ad_id} 已删除。")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"删除失败：{e}")

# ===== 模块注册 =====
def register(app):
    app.add_handler(CommandHandler("推送广告", push_ad))
    app.add_handler(CommandHandler("广告历史", ad_history))
    app.add_handler(CommandHandler("删除广告", delete_ad))
    # 定时广告推送请用调度器定期调用 push_pending_ads
