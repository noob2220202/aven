import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from . import config
from .handlers import match, matches, start

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    config.validate()
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(CommandHandler("help", start.help_command))
    application.add_handler(CommandHandler("matches", matches.matches_command))

    application.add_handler(CallbackQueryHandler(matches.date_callback, pattern=r"^date:"))
    application.add_handler(CallbackQueryHandler(match.match_callback, pattern=r"^match:"))
    application.add_handler(CallbackQueryHandler(match.lineup_callback, pattern=r"^lineup:"))
    application.add_handler(CallbackQueryHandler(match.odds_callback, pattern=r"^odds:"))
    application.add_handler(CallbackQueryHandler(match.comment_callback, pattern=r"^comment:"))
    application.add_handler(CallbackQueryHandler(match.predict_callback, pattern=r"^predict:"))

    return application


def main() -> None:
    application = build_application()
    logger.info("Starting Telegram World Cup bot (polling)...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
