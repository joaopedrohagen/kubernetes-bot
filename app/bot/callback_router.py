from telegram import Update
from telegram.ext import ContextTypes
from app.utils.logger import logger
from app.bot.callbacks.pods import PodCommands
from app.bot.callbacks.secrets import SecretCommands
from app.bot.exceptions import InvalidCallbackData

class Callbacks:
  def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    self.query = update.callback_query
    self.update = update
    self.context = context

    if not self.query or not self.query.data or not self.query.message:
        raise InvalidCallbackData("Callback inválido: mensagem ausente")

    self.chat_id = self.query.message.chat.id

  # @classmethod
  # async def answer(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
  #   self = cls(update, context)
  #   assert self.query is not None
  #   await self.query.answer()
  #   return self

  async def callback_button(self):
    assert self.query and self.query.data is not None

    await self.query.answer()

    try:
      pod_handler = PodCommands(context=self.context, chat_id=self.chat_id, query=self.query)
      secret_handler = SecretCommands(context=self.context, chat_id=self.chat_id, query=self.query)

      if self.query.data.startswith("restart"):
        await pod_handler.restart()

      elif self.query.data.startswith("logs"):
        await pod_handler.logs()

      elif self.query.data.startswith("secrets"):
        await secret_handler.secrets()

      else:
        await self.context.bot.send_message(
          chat_id=self.chat_id,
          text="🔴 Comando desconhecido.",
          parse_mode="Markdown"
        )

    except Exception as e:
      logger.error("Erro ao processar callback.")
      await self.context.bot.send_message(
        chat_id=self.chat_id,
        text="🔴 Erro ao processar ação!",
        parse_mode="Markdown"
      )


