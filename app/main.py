from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from app.bot.handlers import list_secrets, pod_status, callback_button, list_secrets
from app.config.settings import settings
from app.services.kubernetes import load_kube_config

def main():
    load_kube_config(local=True)

    app = ApplicationBuilder().token(settings["telegram_bot_token"]).build()
    app.add_handler(CommandHandler("pod_status", pod_status))
    app.add_handler(CommandHandler("list_secrets", list_secrets))
    app.add_handler(CallbackQueryHandler(callback_button))

    app.run_polling()

if __name__ == "__main__":
    main()
