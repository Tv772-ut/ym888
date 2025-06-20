# commands/wallet.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from models import Wallet, WalletLog, User
from db import session
from sqlalchemy.exc import SQLAlchemyError
from utils import parse_amount, format_amount

# ===== 1. 查询余额 =====
async def wallet_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    with session() as db:
        user = db.query(User).filter_by(tg_id=user_id).first()
        if not user:
            await update.message.reply_text("未找到用户信息，请先使用机器人进行一次操作。")
            return
        wallet = db.query(Wallet).filter_by(user_id=user.id).first()
        if not wallet:
            wallet = Wallet(user_id=user.id, balance=0.0)
            db.add(wallet)
            db.commit()
        await update.message.reply_text(f"当前余额：{format_amount(wallet.balance)}")

# ===== 2. 充值功能 =====
async def wallet_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """用法：/充值 金额"""
    if not context.args:
        await update.message.reply_text("用法：/充值 金额")
        return
    amount, currency = parse_amount(context.args[0])
    if amount <= 0:
        await update.message.reply_text("充值金额必须大于0。")
        return
    user_id = str(update.effective_user.id)
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                user = User(tg_id=user_id)
                db.add(user)
                db.commit()
            wallet = db.query(Wallet).filter_by(user_id=user.id).first()
            if not wallet:
                wallet = Wallet(user_id=user.id, balance=0.0)
                db.add(wallet)
            wallet.balance += amount
            # 记录流水
            log = WalletLog(user_id=user.id, type="deposit", amount=amount, currency=currency)
            db.add(log)
            db.commit()
        await update.message.reply_text(f"充值成功，当前余额：{format_amount(wallet.balance)}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"充值失败：{e}")

# ===== 3. 提现功能 =====
async def wallet_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """用法：/提现 金额"""
    if not context.args:
        await update.message.reply_text("用法：/提现 金额")
        return
    amount, currency = parse_amount(context.args[0])
    if amount <= 0:
        await update.message.reply_text("提现金额必须大于0。")
        return
    user_id = str(update.effective_user.id)
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                await update.message.reply_text("未找到用户信息。")
                return
            wallet = db.query(Wallet).filter_by(user_id=user.id).first()
            if not wallet or wallet.balance < amount:
                await update.message.reply_text("余额不足。")
                return
            wallet.balance -= amount
            log = WalletLog(user_id=user.id, type="withdraw", amount=amount, currency=currency)
            db.add(log)
            db.commit()
        await update.message.reply_text(f"提现成功，当前余额：{format_amount(wallet.balance)}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"提现失败：{e}")

# ===== 4. 用户间转账 =====
async def wallet_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """用法：/转账 金额 @对方用户名"""
    if len(context.args) < 2:
        await update.message.reply_text("用法：/转账 金额 @对方用户名")
        return
    amount, currency = parse_amount(context.args[0])
    if amount <= 0:
        await update.message.reply_text("转账金额必须大于0。")
        return
    recv_username = context.args[1].lstrip('@')
    sender_id = str(update.effective_user.id)
    try:
        with session() as db:
            sender = db.query(User).filter_by(tg_id=sender_id).first()
            receiver = db.query(User).filter_by(username=recv_username).first()
            if not sender or not receiver:
                await update.message.reply_text("收款人不存在。")
                return
            sender_wallet = db.query(Wallet).filter_by(user_id=sender.id).first()
            receiver_wallet = db.query(Wallet).filter_by(user_id=receiver.id).first()
            if not sender_wallet or sender_wallet.balance < amount:
                await update.message.reply_text("余额不足，无法转账。")
                return
            if not receiver_wallet:
                receiver_wallet = Wallet(user_id=receiver.id, balance=0.0)
                db.add(receiver_wallet)
            sender_wallet.balance -= amount
            receiver_wallet.balance += amount
            log_out = WalletLog(user_id=sender.id, type="transfer_out", amount=amount, currency=currency,
                                other_user_id=receiver.id)
            log_in = WalletLog(user_id=receiver.id, type="transfer_in", amount=amount, currency=currency,
                               other_user_id=sender.id)
            db.add_all([log_out, log_in])
            db.commit()
        await update.message.reply_text(f"已成功转账 {format_amount(amount, currency)} 给 @{recv_username}")
    except SQLAlchemyError as e:
        await update.message.reply_text(f"转账失败：{e}")

# ===== 5. 钱包流水明细 =====
async def wallet_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """用法：/流水 [数量]"""
    user_id = str(update.effective_user.id)
    limit = int(context.args[0]) if context.args and context.args[0].isdigit() else 10
    try:
        with session() as db:
            user = db.query(User).filter_by(tg_id=user_id).first()
            if not user:
                await update.message.reply_text("未找到用户信息。")
                return
            logs = (
                db.query(WalletLog)
                .filter_by(user_id=user.id)
                .order_by(WalletLog.created_at.desc())
                .limit(limit)
                .all()
            )
            if not logs:
                await update.message.reply_text("暂无流水。")
                return
            msg = "\n".join(
                [f"{l.created_at:%m-%d %H:%M} {l.type} {format_amount(l.amount, l.currency)}"
                 + (f" 对方:{l.other_user_id}" if l.other_user_id else "")
                 for l in logs]
            )
            await update.message.reply_text("最近流水：\n" + msg)
    except SQLAlchemyError as e:
        await update.message.reply_text(f"查询失败：{e}")

# ===== 注册模块命令 =====
def register(app):
    app.add_handler(CommandHandler("余额", wallet_balance))
    app.add_handler(CommandHandler("充值", wallet_deposit))
    app.add_handler(CommandHandler("提现", wallet_withdraw))
    app.add_handler(CommandHandler("转账", wallet_transfer))
    app.add_handler(CommandHandler("流水", wallet_logs))
