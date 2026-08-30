"""Worker de Telegram. Corre por separado del API (ver docker-compose:
servicio telegram-worker) usando polling -- no requiere dominio publico ni
HTTPS, ideal para esta primera fase corriendo solo en tu red/VM.
"""

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from app.agents.orchestrator import route_document, route_message
from app.config import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram-worker")


def _is_authorized(user) -> bool:
    allowed = settings.allowed_telegram_ids
    if not allowed:
        return True  # sin whitelist configurada, no bloqueamos a nadie
    return user is not None and user.id in allowed


async def _reject_unauthorized(update: Update, user) -> None:
    log.warning("Mensaje rechazado de usuario no autorizado: %s", user.id if user else "desconocido")
    await update.message.reply_text(
        "No estas autorizado para usar este bot todavia. Pedile a Nacho que agregue tu "
        "Telegram user id a TELEGRAM_ALLOWED_USER_IDS."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text if update.message else ""

    if not _is_authorized(user):
        await _reject_unauthorized(update, user)
        return

    reply = route_message(chat_id, text)
    await update.message.reply_text(reply)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not _is_authorized(user):
        await _reject_unauthorized(update, user)
        return

    doc = update.message.document
    if not doc.file_name.lower().endswith(".txt"):
        await update.message.reply_text(
            "Por ahora solo puedo leer archivos CGATS en formato .txt"
        )
        return

    tg_file = await doc.get_file()
    file_bytes = await tg_file.download_as_bytearray()
    content = bytes(file_bytes).decode("utf-8", errors="replace")

    reply = route_document(chat_id, doc.file_name, content)
    await update.message.reply_text(reply)


def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en .env")

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    log.info("Telegram worker arrancando (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
