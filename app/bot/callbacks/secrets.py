from telegram import CallbackQuery
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from app.services.kubernetes import get_secrets_data
from app.bot.exceptions import InvalidCallbackData
from app.utils.logger import logger

class SecretCommands:
  def __init__(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, query: CallbackQuery):
    if not query or not query.data or not query.message:
        raise InvalidCallbackData("Callback inválido: mensagem ausente")

    self.context = context
    self.chat_id = chat_id
    self.query = query
    _, self.namespace, self.secret_name = query.data.split("|")

  async def secrets(self):
    try:
      secret = get_secrets_data(name=self.secret_name, namespace=self.namespace)

      if secret is None:
        await self.context.bot.send_message(
          chat_id=self.chat_id,
          text="🟡 Nenhuma secret encontrada!",
          parse_mode="Markdown"
        )
        return

      lines = [f"{k}={v}" for k, v in secret.items()]
      joined = "\n".join(lines)
      escaped = escape_markdown(joined, version=2)
      data = f"```env\n{escaped}```"

      await self.context.bot.send_message(
          chat_id=self.chat_id,
          text=f"Recuperando as secrets de {self.secret_name}",
          parse_mode="Markdown"
      )

      await self.context.bot.send_message(
          chat_id=self.chat_id,
          text=data,
          parse_mode="MarkdownV2"
      )

    except Exception as e:
        logger.error("Erro ao retornar secrets!")

        await self.context.bot.send_message(
          chat_id=self.chat_id,
          text="🔴 Erro ao recuperar secret!",
          parse_mode="Markdown"
        )
