# commands/wallet_api.py

import os
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# ===== 配置（可放到 config.py）=====
TRC20_USDT_CONTRACT = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"  # USDT 合约地址
TRON_NODE_URL = os.getenv("TRON_NODE_URL", "https://api.trongrid.io")  # 官方主网
MASTER_PRIVATE_KEY = os.getenv("TRON_MASTER_PRIVATE_KEY")  # 机器人资金管理主私钥

# ===== 初始化 Tron 客户端 =====
tron = Tron(network="mainnet", provider=TRON_NODE_URL)

# ===== 1. 生成新钱包地址 =====
def create_wallet():
    priv = PrivateKey.random()
    address = priv.public_key.to_base58check_address()
    return {
        "address": address,
        "private_key": priv.hex(),
    }

# ===== 2. 查询地址 TRC20 USDT 余额（单位为 USDT）=====
def get_trc20_balance(address: str, contract=TRC20_USDT_CONTRACT) -> float:
    contract = tron.get_contract(contract)
    balance = contract.functions.balanceOf(address)
    # USDT 通常6位小数
    return balance / 1_000_000

# ===== 3. 发起 TRC20 USDT 转账 =====
def send_trc20(from_privkey: str, to_address: str, amount: float, contract=TRC20_USDT_CONTRACT) -> str:
    priv = PrivateKey(bytes.fromhex(from_privkey) if len(from_privkey)==64 else bytes.fromhex(from_privkey[2:]))
    contract = tron.get_contract(contract)
    txn = (
        contract.functions.transfer(to_address, int(amount * 1_000_000))
        .with_owner(priv.public_key.to_base58check_address())
        .fee_limit(2_000_000)
        .build()
        .sign(priv)
    )
    result = txn.broadcast().wait()
    if not result['receipt']['result']:
        raise TransactionError(f"转账失败: {result}")
    return result['id']

# ===== 4. 查询TRC20转账记录（简易）=====
def get_trc20_tx_list(address: str, limit=10, contract=TRC20_USDT_CONTRACT):
    # 可用第三方API，如 tronscan
    import requests
    url = f"https://apilist.tronscanapi.com/api/token_trc20/transfers?limit={limit}&start=0&sort=-timestamp&count=true&filterTokenValue=0&relatedAddress={address}&contract_address={contract}"
    r = requests.get(url)
    data = r.json()
    return [
        {
            "hash": t['transaction_id'],
            "from": t['from_address'],
            "to": t['to_address'],
            "value": int(t['quant']) / 1_000_000,
            "timestamp": t['block_ts']//1000,
            "confirmed": t.get('confirmed', True)
        } for t in data.get('data', [])
    ]

# ========== Telegram 指令示例 ==========
async def wallet_create_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """生成新钱包地址"""
    w = create_wallet()
    await update.message.reply_text(f"🎉 你的新 TRC20 地址：\n{w['address']}\n私钥(请妥善保管)：\n{w['private_key']}")

async def wallet_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查询 USDT 余额 /余额TRC20 地址"""
    if not context.args:
        await update.message.reply_text("用法：/余额TRC20 地址")
        return
    try:
        address = context.args[0]
        bal = get_trc20_balance(address)
        await update.message.reply_text(f"{address}\nUSDT余额：{bal:.6f} USDT")
    except Exception as e:
        await update.message.reply_text(f"查询失败：{e}")

async def wallet_send_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """USDT转账 /转账TRC20 私钥 对方地址 金额"""
    if len(context.args) < 3:
        await update.message.reply_text("用法：/转账TRC20 私钥 对方地址 金额")
        return
    try:
        priv, to, amount = context.args[0], context.args[1], float(context.args[2])
        txid = send_trc20(priv, to, amount)
        await update.message.reply_text(f"转账成功，交易ID:\n{txid}")
    except Exception as e:
        await update.message.reply_text(f"转账失败：{e}")

async def wallet_txlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查询最近转账记录 /流水TRC20 地址 [数量]"""
    if not context.args:
        await update.message.reply_text("用法：/流水TRC20 地址 [数量]")
        return
    address = context.args[0]
    limit = int(context.args[1]) if len(context.args)>1 and context.args[1].isdigit() else 5
    try:
        txs = get_trc20_tx_list(address, limit=limit)
        if not txs:
            await update.message.reply_text("暂无转账记录。")
            return
        msg = "\n\n".join([f"时间:{t['timestamp']}\nFrom:{t['from']}\nTo:{t['to']}\n金额:{t['value']}" for t in txs])
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"查询失败：{e}")

# ===== 注册 =====
def register(app):
    app.add_handler(CommandHandler("新钱包", wallet_create_cmd))
    app.add_handler(CommandHandler("余额TRC20", wallet_balance_cmd))
    app.add_handler(CommandHandler
