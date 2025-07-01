from telegram import Update
from telegram.ext import ContextTypes
from app.services.kubernetes import get_pods
from app.utils.logger import logger

class CustomBotError(Exception):
    pass

async def pod_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        raise CustomBotError("Usuário não encontrado")

    if not update.message:
        raise CustomBotError("Mensagem não encontrada")

    user = update.effective_user.first_name
    args = context.args

    if not args:
        await update.message.reply_text("Você não passou nenhum namespace.")
        return

    namespace = args[0]
    await update.message.reply_text(f"Olá {user}! Listando pods no namespace: {namespace}")

    try:
        pods = get_pods(namespace)
        for pod in pods:
            await update.message.reply_text(
                f"POD: {pod.name}\nNamespace: {pod.ns}\nStatus: {pod.status}"
            )
    except Exception as e:
        logger.error(f"Erro ao buscar pods: {e}")
        await update.message.reply_text("Erro ao buscar os pods.")
