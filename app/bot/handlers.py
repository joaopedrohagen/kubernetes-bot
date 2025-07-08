from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from app.services.kubernetes import get_pods, delete_pods, pod_logs
from app.utils.logger import logger

class CustomBotError(Exception):
    pass

async def callback_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not query or not query.data or not query.message:
        raise CustomBotError("Callback inválido: mensagem ausente")

    await query.answer()

    chat_id = query.message.chat.id

    if query.data.startswith("restart"):
        try:
            _, namespace, pod_name = query.data.split("|")
            delete_pods(namespace=namespace, pod_name=pod_name)
            await context.bot.send_message(chat_id=chat_id, text=f"🟢 Pod {pod_name} reiniciado!", parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Erro ao deletar recurso!")
            await context.bot.send_message(chat_id=chat_id, text="🔴 Erro ao deletar pod!", parse_mode="Markdown")

    if query.data.startswith("logs"):
        try:
            _, namespace, pod_name = query.data.split("|")
            logs = pod_logs(namespace=namespace, pod_name=pod_name)

            if not logs:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🟡 Nenhum log de {pod_name}! Talvez não tenha logs."
                )
                return

            logs_safe = escape_markdown(logs, version=2)
            MAX_LEN = 3900
            logs_safe = logs_safe[-MAX_LEN:]

            text = f"```terminal\n{logs_safe}```"

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Retornando os logs de {pod_name}",
                parse_mode="Markdown"
                )

            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="MarkdownV2"
            )

        except Exception as e:
            logger.error(f"Erro ao retornar logs!")
            await context.bot.send_message(chat_id=chat_id, text="🔴 Erro ao recuperar log!", parse_mode="Markdown")

async def pod_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        raise CustomBotError("Usuário não encontrado")

    if not update.message:
        raise CustomBotError("Mensagem não encontrada")

    user = update.effective_user.first_name
    args = context.args

    if not args:
        await update.message.reply_text("🟡 Você não passou nenhum namespace.")
        return

    namespace = args[0]
    await update.message.reply_text(
        f"Olá {user}! 😄 \n"
        f"Listando pods no namespace {namespace}..."
    )

    try:
        pods = get_pods(namespace)
        for pod in pods:
            keyboard = [
                [
                    InlineKeyboardButton("Restart 🔁", callback_data=f"restart|{pod.ns}|{pod.name}"),
                    InlineKeyboardButton("Logs 📄", callback_data=f"logs|{pod.ns}|{pod.name}")
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"POD: {pod.name}\nNamespace: {pod.ns}\nStatus: {pod.status}", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Erro ao buscar pods: {e}")
        await update.message.reply_text("🔴 Erro ao buscar os pods.")
