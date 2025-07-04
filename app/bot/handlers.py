from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.kubernetes import get_pods, delete_pods
from app.utils.logger import logger

class CustomBotError(Exception):
    pass

async def callback_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not query or not query.data:
        raise CustomBotError("Sem Callback")

    await query.answer()

    if query.data.startswith("restart"):
        try:
            _, namespace, pod_name = query.data.split("|")
            delete_pods(namespace=namespace, label=pod_name)
            await query.edit_message_text(f"Pod {pod_name} reiniciado!", parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Erro ao deletar recurso!")
            await query.edit_message_text(f"Erro ao deletar pod!")


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
            keyboard = [
                [InlineKeyboardButton("Restart", callback_data=f"restart|{pod.ns}|{pod.name}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"POD: {pod.name}\nNamespace: {pod.ns}\nStatus: {pod.status}", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Erro ao buscar pods: {e}")
        await update.message.reply_text("Erro ao buscar os pods.")
