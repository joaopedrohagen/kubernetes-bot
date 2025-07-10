from telegram import CallbackQuery
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from app.services.kube_client import kube_client as kube
from app.bot.exceptions import InvalidCallbackData
from app.utils.logger import logger

class ConfigMapCommands:
  def __init__(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, query: CallbackQuery):
    if not query or not query.data or not query.message:
        raise InvalidCallbackData("Callback inválido: mensagem ausente")

    self.context = context
    self.chat_id = chat_id
    self.query = query
    _, self.namespace, self.configmap_name = query.data.split("|")

  async def configmaps(self):
    try:
      configmap = kube.get_config_map_data(name=self.configmap_name, namespace=self.namespace)

      if configmap is None:
        await self.context.bot.send_message(
          chat_id=self.chat_id,
          text="🟡 Nenhum configmap encontrado!",
          parse_mode="Markdown"
        )
        return

      lines = [f"{k}={v}" for k, v in configmap.items()]
      joined = "\n".join(lines)
      escaped = escape_markdown(joined, version=2)
      data = f"```env\n{escaped}```"

      await self.context.bot.send_message(
          chat_id=self.chat_id,
          text=f"Recuperando as configmaps de {self.configmap_name}",
          parse_mode="Markdown"
      )

      await self.context.bot.send_message(
          chat_id=self.chat_id,
          text=data,
          parse_mode="MarkdownV2"
      )

    except Exception as e:
        logger.error("Erro ao retornar configmaps!")

        await self.context.bot.send_message(
          chat_id=self.chat_id,
          text="🔴 Erro ao recuperar configmap!",
          parse_mode="Markdown"
        )
