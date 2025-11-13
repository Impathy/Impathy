import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import config
from database.tutors_db import TutorsDB
from database.sheets_manager import SheetsManager
from handlers.auth import setup_auth_handlers


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)

logger = logging.getLogger(__name__)


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /health command - returns bot status."""
    await update.message.reply_text(
        "✅ Bot is running and healthy!\n"
        f"Credentials path: {config.CREDENTIALS_PATH}\n"
        f"Tutors config path: {config.TUTORS_CONFIG_PATH}"
    )


def main():
    """Start the bot."""
    logger.info("Starting Telegram bot...")
    
    try:
        config.validate_config()
    except (ValueError, FileNotFoundError) as e:
        logger.warning(f"Configuration validation failed: {e}")
        logger.info("Continuing without validation for development purposes...")
    
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Initialize database managers
    tutors_db = TutorsDB(config.TUTORS_CONFIG_PATH)
    sheets_manager = SheetsManager(config.CREDENTIALS_PATH)
    
    application.add_handler(CommandHandler(config.BotCommands.HEALTH.value, health_command))
    
    # Set up auth handlers (start, register, profile, help)
    setup_auth_handlers(application, tutors_db, sheets_manager)
    
    logger.info("Bot initialized successfully. Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
