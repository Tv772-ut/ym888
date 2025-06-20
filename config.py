from telegram.ext import Application
from config import BOT_TOKEN
from db import init_db

# 各功能模块
import commands.account
import commands.admin
import commands.notify
import commands.ad
import commands.wallet
import commands.watermarker
import commands.finance
import commands.group
import commands.help

def main():
    # 初始化数据库（只需首次启动时建表）
    init_db()

    # 创建 Telegram 应用
    app = Application.builder().token(BOT_TOKEN).build()

    # 注册各模块的 handler
    commands.account.register(app)
    commands.admin.register(app)
    commands.notify.register(app)
    commands.ad.register(app)
    commands.wallet.register(app)
    commands.watermarker.register(app)
    commands.finance.register(app)
    commands.group.register(app)
    commands.help.register(app)

    print("Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
