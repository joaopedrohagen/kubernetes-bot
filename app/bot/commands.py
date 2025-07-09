from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.kube_client import kube_client as kube
from app.utils.logger import logger
from app.bot.exceptions import MissingMessage, MissingArgs

class UserCommands:
  def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    self.update = update
    self.context = context
    self.args = context.args

  async def pod_status(self):
    if not self.update.message:
      raise MissingMessage("Mensagem não encontrada!")

    if not self.args:
      await self.update.message.reply_text("🟡 Você não passou nenhum namespace.")
      raise MissingArgs ("Argumento não encontrado!")

    namespace = self.args[0]
    await self.update.message.reply_text(f"Listando pods no namespace {namespace}...")

    try:
      pods = kube.get_pods(namespace)

      for pod in pods:
        keyboard = [
          [
            InlineKeyboardButton("Restart 🔁", callback_data=f"restart|{pod.ns}|{pod.name}"),
            InlineKeyboardButton("Logs 📄", callback_data=f"logs|{pod.ns}|{pod.name}")
          ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await self.update.message.reply_text(f"POD: {pod.name}\nNamespace: {pod.ns}\nStatus: {pod.status}", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Erro ao buscar pods: {e}")
        await self.update.message.reply_text("🔴 Erro ao buscar os pods.")

  async def list_envs(self):
    if not self.update.message:
      raise MissingMessage("Mensagem não encontrada!")

    if not self.args:
      await self.update.message.reply_text("🟡 Você não passou nenhum namespace.")
      raise MissingArgs ("Argumento não encontrado!")

    namespace = self.args[0]
    await self.update.message.reply_text(f"Listando secrets no namespace {namespace}")

    try:
      secrets = kube.get_secrets(namespace)
      for secret in secrets:
        keyboard = [
          [
            InlineKeyboardButton("Secrets 🔐", callback_data=f"secrets|{secret.ns}|{secret.name}")
          ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await self.update.message.reply_text(f"Secret: {secret.name}\nNamespace: {secret.ns}", reply_markup=reply_markup)

    except Exception as e:
      logger.error(f"Erro ao buscar secret: {e}")
      await self.update.message.reply_text("🔴 Erro ao buscar as secrets.")

