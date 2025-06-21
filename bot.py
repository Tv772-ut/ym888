# ym888/bot.py
import logging
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_TOKEN
from commands import base, account, admin, notify, ad, wallet, watermarker, finance, group, help as help_cmd

def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # 注册命令
    app.add_handler(CommandHandler("start", base.start))
    app.add_handler(CommandHandler("help", help_cmd.help_command))
    app.add_handler(CommandHandler("account", account.account_command))
    # ... 其他命令注册

    app.run_polling()

if __name__ == "__main__":
    main()
