# commands/exchange_api.py

import httpx
import asyncio
from aiocache import cached, Cache
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# ===== 配置：可添加自己的API KEY或地址 =====
DEFAULT_FIAT_API = "https://api.exchangerate.host/latest"
DEFAULT_CRYPTO_API = "https://api.coingecko.com/api/v3/simple/price"

# ===== 汇率缓存：防抖动，60秒自动过期 =====
@cached(ttl=60, cache=Cache.MEMORY)
async def get_fiat_rate(base: str, quote: str) -> float:
    async with httpx.AsyncClient() as client:
        params = {"base": base.upper(), "symbols": quote.upper()}
        resp = await client.get(DEFAULT_FIAT_API, params=params, timeout=8)
        data = resp.json()
        return data["rates"][quote.upper()]

@cached(ttl=60, cache=Cache.MEMORY)
async def get_crypto_price(coin: str, vs: str) -> float:
    async with httpx.AsyncClient() as client:
        params = {"ids": coin.lower(), "vs_currencies": vs.lower()}
        resp = await client.get(DEFAULT_CRYPTO_API, params=params, timeout=8)
        data = resp.json()
        return data[coin.lower()][vs.lower()]

# ===== 智能币价查询（自动判断法币还是加密货币） =====
async def exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    用法：/汇率 usd cny
         /汇率 btc usd
         /汇率 eth cny
    """
    if len(context.args) < 2:
        await update.message.reply_text("用法：/汇率 币种1 币种2\n例如：/汇率 usd cny、/汇率 btc usd")
        return
    base = context.args[0].lower()
    quote = context.args[1].lower()

    fiat_set = {"usd", "cny", "eur", "jpy", "gbp", "hkd", "twd", "aud", "cad", "sgd", "rub"}
    crypto_set = {"btc", "eth", "usdt", "bch", "doge", "sol", "trx", "fil", "ltc", "dot", "ada", "matic"}

    try:
        if base in fiat_set and quote in fiat_set:
            rate = await get_fiat_rate(base, quote)
            await update.message.reply_text(f"💱 {base.upper()} → {quote.upper()} 汇率：{rate:.4f}")
        elif base in crypto_set or quote in crypto_set:
            # 主流币 → 法币 或主流币之间
            coin, vs = (base, quote) if base in crypto_set else (quote, base)
            price = await get_crypto_price(coin, vs)
            await update.message.reply_text(f"₿ {coin.upper()} → {vs.upper()} 现价：{price:.6f}")
        else:
            # 尝试法币API
            try:
                rate = await get_fiat_rate(base, quote)
                await update.message.reply_text(f"💱 {base.upper()} → {quote.upper()} 汇率：{rate:.4f}")
            except Exception:
                # fallback: CoinGecko试一下
                price = await get_crypto_price(base, quote)
                await update.message.reply_text(f"₿ {base.upper()} → {quote.upper()} 现价：{price:.6f}")
    except Exception as e:
        await update.message.reply_text(f"查询失败：{e}")

# ===== 批量行情功能（可选）=====
async def multi_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    批量查询主流币对，例如 /批量汇率 btc,eth,sol usd
    """
    if len(context.args) < 2:
        await update.message.reply_text("用法：/批量汇率 btc,eth,sol usd")
        return
    coins = context.args[0].lower().split(",")
    vs = context.args[1].lower()
    tasks = [get_crypto_price(c, vs) for c in coins]
    try:
        prices = await asyncio.gather(*tasks)
        msg = "\n".join([f"{c.upper()} → {vs.upper()} : {p}" for c, p in zip(coins, prices)])
        await update.message.reply_text("主流币行情：\n" + msg)
    except Exception as e:
        await update.message.reply_text(f"批量行情查询失败：{e}")

# ===== 注册命令 =====
def register(app):
    app.add_handler(CommandHandler("汇率", exchange_command))
    app.add_handler(CommandHandler("批量汇率", multi_exchange))

# ====== 高级说明 ======
"""
- 支持任意币种对（主流法币、主流加密货币，自动路由API）
- 采用 httpx+aiocache，异步高速，缓存防止API限制
- 可扩展更多币种、API、行情源
- 推荐配合定时行情推送/告警功能
"""
