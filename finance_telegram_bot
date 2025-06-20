from telegram.ext import Application, CommandHandler, MessageHandler, filters
import config
from commands import account, admin, notify, ad, wallet, watermarker, finance, group, help

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # 注册处理器
    app.add_handler(MessageHandler(filters.ALL, account.handle_account))
    app.add_handler(MessageHandler(filters.ALL, admin.handle_admin))
    app.add_handler(MessageHandler(filters.ALL, notify.handle_notify))
    app.add_handler(MessageHandler(filters.ALL, ad.handle_ad))
    app.add_handler(MessageHandler(filters.ALL, wallet.handle_wallet))
    app.add_handler(MessageHandler(filters.ALL, watermarker.handle_watermark))
    app.add_handler(MessageHandler(filters.ALL, finance.handle_finance))
    app.add_handler(MessageHandler(filters.ALL, group.handle_group))
    app.add_handler(MessageHandler(filters.ALL, help.handle_help))
    
    print("Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
