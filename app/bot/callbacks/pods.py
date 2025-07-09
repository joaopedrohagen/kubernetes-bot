from telegram import CallbackQuery
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from app.services.kube_client import kube_client as kube
from app.bot.exceptions import InvalidCallbackData
from app.utils.logger import logger

class PodCommands:
  def __init__(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, query: CallbackQuery):
    if not query or not query.data or not query.message:
        raise InvalidCallbackData("Callback inválido: mensagem ausente")

    self.context = context
    self.chat_id = chat_id
    self.query = query
    _, self.namespace, self.pod_name = query.data.split("|")

  async def restart(self):
    try:
      kube.delete_pods(namespace=self.namespace, pod_name=self.pod_name)
      await self.context.bot.send_message(chat_id=self.chat_id, text=f"🟢 Pod {self.pod_name} reiniciado!", parse_mode="Markdown")

    except Exception as e:
      logger.error(f"Erro ao deletar recurso!")
      await self.context.bot.send_message(chat_id=self.chat_id, text="🔴 Erro ao deletar pod!", parse_mode="Markdown")

  async def logs(self):
    try:
      logs = kube.pod_logs(namespace=self.namespace, pod_name=self.pod_name)

      if logs is None:
        await self.context.bot.send_message(
            chat_id=self.chat_id,
            text=f"🟡 Nenhum log de {self.pod_name}! Talvez não tenha logs."
        )
        return

      logs_safe = escape_markdown(logs, version=2)
      MAX_LEN = 3900
      logs_safe = logs_safe[-MAX_LEN:]

      text = f"```terminal\n{logs_safe}```"

      await self.context.bot.send_message(
          chat_id=self.chat_id,
          text=f"Retornando os logs de {self.pod_name}",
          parse_mode="Markdown"
          )

      await self.context.bot.send_message(
          chat_id=self.chat_id,
          text=text,
          parse_mode="MarkdownV2"
      )

    except Exception as e:
        logger.error("Erro ao retornar logs!")
        await self.context.bot.send_message(chat_id=self.chat_id, text="🔴 Erro ao recuperar log!", parse_mode="Markdown")

