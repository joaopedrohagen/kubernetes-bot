from types import LambdaType
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.kube_client import kube_client as kube
from app.services.kubernetes import KubeResourceInfo
from app.utils.logger import logger
from app.bot.exceptions import MissingMessage, MissingArgs

class UserCommands:
  def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    self.update = update
    self.context = context
    self.args = context.args

  async def _verify_namespace(self):
    if not self.update.message:
      raise MissingMessage("Mensagem não encontrada!")

    if not self.args:
      await self.update.message.reply_text("🟡 Você não passou nenhum namespace.")
      raise MissingArgs ("Argumento não encontrado!")

    return self.args[0]

  async def _list_resources(self, resource: str, resource_list: list[KubeResourceInfo], buttons: Dict[str, str], func_message: LambdaType):
    if not self.update.message:
      raise MissingMessage("Mensagem não encontrada!")

    if not self.args:
      await self.update.message.reply_text("🟡 Você não passou nenhum namespace.")
      raise MissingArgs ("Argumento não encontrado!")

    namespace = await self._verify_namespace()
    await self.update.message.reply_text(f"Listando {resource} no namespace {namespace}...")

    try:
      for r in resource_list:
        keyboard = [[
          InlineKeyboardButton(f"{value}", callback_data=f"{key}|{r.ns}|{r.name}")
          for key, value in buttons.items()
        ]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await self.update.message.reply_text(f"{func_message(r)}", reply_markup=reply_markup)

    except Exception as e:
      logger.error(f"Erro ao buscar pods: {e}")
      await self.update.message.reply_text(f"🔴 Erro ao buscar {resource}.")


  async def pod_status(self):
    namespace = await self._verify_namespace()
    pods = kube.get_pods(namespace)
    resource = "pods"
    func_message = lambda pod: f"POD: {pod.name}\nNamespace: {pod.ns}\nStatus: {pod.status}"
    buttons = {
      "restart": "Restart 🔁",
      "logs": "Logs 📄"
    }

    await self._list_resources(resource=resource, resource_list=pods, func_message=func_message, buttons=buttons)


  async def list_secrets(self):
    namespace = await self._verify_namespace()
    secrets = kube.get_secrets(namespace)
    resource = "secrets"
    func_message = lambda secret: f"Secret: {secret.name}\nNamespace: {secret.ns}"
    buttons = {
      "secrets": "Secrets 🔐"
    }

    await self._list_resources(resource=resource, resource_list=secrets, func_message=func_message, buttons=buttons)

  async def list_config_maps(self):
    namespace = await self._verify_namespace()
    configmap = kube.get_config_map(namespace)
    resource = "configmaps"
    func_message = lambda cm: f"ConfigMap: {cm.name}\nNamespace: {cm.ns}"
    buttons = {
      "configmaps": "ConfigMap ⚙️"
    }

    await self._list_resources(resource=resource, resource_list=configmap, func_message=func_message, buttons=buttons)

