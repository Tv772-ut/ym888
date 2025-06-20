# commands/notify.py

from telegram import Update, ChatMember, Chat, ChatMemberUpdated
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ChatMemberHandler
from models import Announcement, Group
from db import session
from sqlalchemy.exc import SQLAlchemyError
import datetime

# == 1. 欢迎新成员 ==
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member.new_chat_member
    if member.status in (ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR):
        chat = update.effective_chat
        welcome_text = f"🎉 欢迎 @{member.user.username or member.user.first_name} 加入【{chat.title}】！\n输入 /help 查看功能说明。"
        await context.bot.send_message(chat_id=chat.id, text=welcome_text)

# == 2. 发布群组公告（仅群主/管理员可用） ==
async def group_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/公告 内容")
        return
    group_id = str(update.effective_chat.id)
    content = " ".join(context.args)
    sender_id = str(update.effective_user.id)
    try:
        with session() as db:
            group = db.query(Group).filter_by(group_id=group_id).first()
            if not group:
                await update.message.reply_text("请先注册群组后再发布公告。")
                return
            # 权限检查：仅群主或管理员可公告
            if group.owner_id != sender_id:
                await update.message.reply_text("只有群主可发布公告。")
                return
            ann = Announcement(group_id=group_id, content=content)
            db.add(ann)
            db.commit()
        await update.message.reply_text("✅ 公告已发布。")
        # 广播到群
        await context.bot.send_message(chat_id=group_id, text=f"📢 群公告：{content}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"公告发布失败：{e}")

# == 3. 定时提醒/自动公告推送（示意，需配合调度器/定时任务实现） ==
async def push_pending_announcements(context: ContextTypes.DEFAULT_TYPE):
    # 定时任务入口：推送未发送的公告
    try:
        with session() as db:
            anns = db.query(Announcement).filter_by(sent=False).all()
            for ann in anns:
                await context.bot.send_message(chat_id=ann.group_id, text=f"📢 群公告：{ann.content}")
                ann.sent = True
            db.commit()
    except SQLAlchemyError as e:
        print(f"[定时公告失败] {e}")

# == 4. 小组/群组欢迎语设置 ==
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """仅群主可设置本群欢迎语 /设置欢迎 欢迎大家！"""
    group_id = str(update.effective_chat.id)
    sender_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("用法：/设置欢迎 欢迎语内容")
        return
    welcome_text = " ".join(context.args)
    try:
        with session() as db:
            group = db.query(Group).filter_by(group_id=group_id).first()
            if not group:
                await update.message.reply_text("群组未注册。")
                return
            if group.owner_id != sender_id:
                await update.message.reply_text("仅群主可设置欢迎语。")
                return
            group.welcome_text = welcome_text
            db.commit()
        await update.message.reply_text("欢迎语已设置。")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"设置失败：{e}")

# == 5. 新成员入群自动触发欢迎语（如已设置） ==
async def custom_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member.new_chat_member
    if member.status in (ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR):
        chat = update.effective_chat
        with session() as db:
            group = db.query(Group).filter_by(group_id=str(chat.id)).first()
            if group and getattr(group, "welcome_text", None):
                await context.bot.send_message(chat_id=chat.id, text=group.welcome_text)
            else:
                # 默认欢迎
                welcome_text = f"🎉 欢迎 @{member.user.username or member.user.first_name} 加入【{chat.title}】！"
                await context.bot.send_message(chat_id=chat.id, text=welcome_text)

# == 注册本模块所有 handler ==
def register(app):
    app.add_handler(CommandHandler("公告", group_announcement))
    app.add_handler(CommandHandler("设置欢迎", set_welcome))
    # 监听新成员变动（Telegram v20+推荐使用 ChatMemberHandler）
    app.add_handler(ChatMemberHandler(custom_welcome, ChatMemberHandler.CHAT_MEMBER))
    # 你还可以根据需要注册 push_pending_announcements 到定时任务队列
