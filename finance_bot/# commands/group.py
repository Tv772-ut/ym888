# commands/group.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from models import Group, User, Bill
from db import session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
import datetime

# =========== 1. 群发消息 ===========
async def group_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """管理员群发消息，用法：/群发 分组名 消息内容"""
    if len(context.args) < 2:
        await update.message.reply_text("用法：/群发 分组名 消息内容")
        return
    group_tag = context.args[0]
    content = " ".join(context.args[1:])
    try:
        with session() as db:
            groups = db.query(Group).filter_by(tag=group_tag).all()
            if not groups:
                await update.message.reply_text("未找到该分组下的群。")
                return
            for group in groups:
                try:
                    await context.bot.send_message(chat_id=group.group_id, text=f"【群发通知】\n{content}")
                except Exception as e:
                    await update.message.reply_text(f"发送到 {group.group_name or group.group_id} 失败: {e}")
            await update.message.reply_text(f"已群发到 {len(groups)} 个群。")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"数据库操作失败：{e}")

# =========== 2. 分组管理 ===========
async def set_group_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """为群设置分组标签，用法：/分组设置 群名 标签"""
    if len(context.args) < 2:
        await update.message.reply_text("用法：/分组设置 群名 标签")
        return
    group_name, tag = context.args[0], context.args[1]
    try:
        with session() as db:
            group = db.query(Group).filter_by(group_name=group_name).first()
            if not group:
                await update.message.reply_text("未找到该群。")
                return
            group.tag = tag
            db.commit()
        await update.message.reply_text(f"群【{group_name}】已设置分组标签：{tag}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"分组设置失败：{e}")

async def list_groups_by_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出某分组下所有群，用法：/分组列表 标签"""
    if not context.args:
       
