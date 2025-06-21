# finance_bot/bot.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from finance_bot.config import settings
from finance_bot.commands import base, account, help as help_cmd

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", base.start))
    application.add_handler(CommandHandler("help", help_cmd.help_command))
    application.add_handler(CommandHandler("记账", account.add_expense))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), base.handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
