# commands/admin.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ADMINS
from models import Group, User
from db import session
from sqlalchemy.exc import SQLAlchemyError

# ===== 权限校验装饰器 =====
def admin_required(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in ADMINS:
            await update.message.reply_text("⚠️ 仅管理员可操作本命令。")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ===== 群组注册/绑定 =====
@admin_required
async def bind_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """管理员绑定群组，群内发送 /注册群组"""
    group_id = str(update.effective_chat.id)
    group_name = update.effective_chat.title or ""
    owner_id = str(update.effective_user.id)
    try:
        with session() as db:
            group = db.query(Group).filter_by(group_id=group_id).first()
            if not group:
                group = Group(group_id=group_id, group_name=group_name, owner_id=owner_id)
                db.add(group)
                db.commit()
                await update.message.reply_text(f"✅ 群组已注册：{group_name}")
            else:
                await update.message.reply_text(f"群组已存在：{group.group_name or group_id}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"数据库操作失败: {e}")

# ===== 群组列表（仅所有者/管理员）=====
@admin_required
async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出所有已注册群组"""
    try:
        with session() as db:
            groups = db.query(Group).all()
            if not groups:
                await update.message.reply_text("暂无已注册群组。")
                return
            msg = "\n".join([f"{g.group_name or g.group_id} (ID: {g.group_id})" for g in groups])
            await update.message.reply_text(f"已注册群组：\n{msg}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"查询失败: {e}")

# ===== 群组分组（示意功能，可扩展为更复杂的分组管理）=====
@admin_required
async def set_group_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """为群组设置标签，如 /设置分组 财务群 标签A"""
    if len(context.args) < 2:
        await update.message.reply_text("用法：/设置分组 <群名> <标签>")
        return
    group_name, tag = context.args[0], context.args[1]
    try:
        with session() as db:
            group = db.query(Group).filter_by(group_name=group_name).first()
            if not group:
                await update.message.reply_text("未找到对应群组。")
                return
            group.tag = tag
            db.commit()
        await update.message.reply_text(f"群组【{group_name}】标签已设置为：{tag}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"设置失败: {e}")

# ===== 管理员设置（添加/移除管理员）=====
@admin_required
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """添加管理员 /添加管理员 12345678"""
    if not context.args:
        await update.message.reply_text("用法：/添加管理员 <用户ID>")
        return
    new_admin = context.args[0].strip()
    if new_admin in ADMINS:
        await update.message.reply_text("该用户已是管理员。")
        return
    # 直接在环境变量/配置维护更安全，这里简单演示
    ADMINS.append(new_admin)
    await update.message.reply_text(f"已添加管理员：{new_admin}")

@admin_required
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """移除管理员 /移除管理员 12345678"""
    if not context.args:
        await update.message.reply_text("用法：/移除管理员 <用户ID>")
        return
    admin_id = context.args[0].strip()
    if admin_id not in ADMINS:
        await update.message.reply_text("该用户不是管理员。")
        return
    ADMINS.remove(admin_id)
    await update.message.reply_text(f"已移除管理员：{admin_id}")

# ===== 用户设置（如昵称、通知开关等）=====
async def set_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """用户自助设置，如 /设置昵称 小明"""
    if len(context.args) < 2:
        await update.message.reply_text("用法：/设置 <字段> <值>（如：/设置 昵称 小明）")
        return
    field, value = context.args[0], " ".join(context.args[1:])
    user_id = str(update.effective_user.id)
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                user = User(tg_id=user_id)
                db.add(user)
            if field in ("昵称", "name", "username"):
                user.username = value
            # 其它字段可扩展
            db.commit()
        await update.message.reply_text(f"已设置{field}为：{value}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"设置失败: {e}")

# ===== 注册模块命令 =====
def register(app):
    app.add_handler(CommandHandler("注册群组", bind_group))
    app.add_handler(CommandHandler("群组列表", list_groups))
    app.add_handler(CommandHandler("设置分组", set_group_tag))
    app.add_handler(CommandHandler("添加管理员", add_admin))
    app.add_handler(CommandHandler("移除管理员", remove_admin))
    app.add_handler(CommandHandler("设置", set_profile))
