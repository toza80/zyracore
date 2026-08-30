"""Worker de Telegram. Corre por separado del API (ver docker-compose:
servicio telegram-worker) usando polling -- no requiere dominio publico ni
HTTPS, ideal para esta primera fase corriendo solo en tu red/VM.
"""

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from app.agents.orchestrator import route_message
from app.config import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram-worker")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text if update.message else ""

    allowed = settings.allowed_telegram_ids
    if allowed and (user is None or user.id not in allowed):
        log.warning("Mensaje rechazado de usuario no autorizado: %s", user.id if user else "desconocido")
        await update.message.reply_text(
            "No estas autorizado para usar este bot todavia. Pedile a Nacho que agregue tu "
            "Telegram user id a TELEGRAM_ALLOWED_USER_IDS."
        )
        return

    reply = route_message(chat_id, text)
    await update.message.reply_text(reply)


def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en .env")

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    log.info("Telegram worker arrancando (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
