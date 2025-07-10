from typing import Any
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from app.bot.commands import UserCommands
from app.bot.callback_router import Callbacks
from app.config.settings import settings
from telegram import BotCommand

async def set_bot_commands(app: Any):
    await app.bot.set_my_commands(
        [
            BotCommand("pod_status", "Lista os pods no namespace passado como argumento."),
            BotCommand("list_envs", "Lista as secrets e os configmaps no namespace passado como argumento.")
        ]
    )

def main():
    app = ApplicationBuilder().token(settings["telegram_bot_token"]).post_init(set_bot_commands).build()

    app.add_handler(CommandHandler("pod_status", lambda update, context: UserCommands(update, context).pod_status()))
    app.add_handler(CommandHandler("list_envs", lambda update, context: UserCommands(update, context).list_envs()))
    app.add_handler(CallbackQueryHandler(lambda update, context: Callbacks(update, context).callback_button()))

    app.run_polling()

if __name__ == "__main__":
    main()
