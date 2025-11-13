"""Authentication and registration handlers for the Telegram bot."""

import logging
from datetime import datetime
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
from database.tutors_db import TutorsDB
from database.sheets_manager import SheetsManager
from database.exceptions import (
    TutorAlreadyExistsError,
    TutorNotFoundError,
    SheetNotFoundError,
    WorksheetNotFoundError,
)
from utils.messages import Messages
from utils.validators import extract_sheet_id, validate_name, sanitize_name

logger = logging.getLogger(__name__)

# Conversation states
AWAITING_NAME, AWAITING_SHEET = range(2)


class AuthHandlers:
    """Handlers for authentication and registration."""

    def __init__(self, tutors_db: TutorsDB, sheets_manager: SheetsManager):
        """Initialize auth handlers.

        Args:
            tutors_db: TutorsDB instance for managing tutor configurations.
            sheets_manager: SheetsManager instance for managing Google Sheets.
        """
        self.tutors_db = tutors_db
        self.sheets_manager = sheets_manager

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command.

        Differentiates between registered and new tutors.
        """
        telegram_id = str(update.effective_user.id)

        try:
            tutor = self.tutors_db.get_tutor(telegram_id)
            # Tutor is already registered
            message = Messages.START_WELCOME_REGISTERED.format(name=tutor.name)
            reply_markup = ReplyKeyboardMarkup(
                [["/profile"], ["/help"]],
                resize_keyboard=True,
                one_time_keyboard=False,
            )
            await update.message.reply_text(message, reply_markup=reply_markup)
        except TutorNotFoundError:
            # New tutor - offer registration
            message = Messages.START_WELCOME_NEW
            reply_markup = ReplyKeyboardMarkup(
                [["/register"], ["/help"]],
                resize_keyboard=True,
                one_time_keyboard=False,
            )
            await update.message.reply_text(message, reply_markup=reply_markup)

    async def register_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the registration conversation."""
        telegram_id = str(update.effective_user.id)

        try:
            tutor = self.tutors_db.get_tutor(telegram_id)
            # User is already registered
            message = Messages.REGISTER_ALREADY_REGISTERED.format(name=tutor.name)
            await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        except TutorNotFoundError:
            # Proceed with registration
            message = Messages.REGISTER_ASK_NAME
            await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
            return AWAITING_NAME

    async def register_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle name input during registration."""
        name = update.message.text.strip() if update.message.text else ""

        if not validate_name(name):
            await update.message.reply_text(Messages.ERROR_INVALID_INPUT)
            await update.message.reply_text(Messages.REGISTER_ASK_NAME)
            return AWAITING_NAME

        name = sanitize_name(name)
        context.user_data["name"] = name

        message = Messages.REGISTER_ASK_SHEET.format(name=name)
        await update.message.reply_text(message)
        return AWAITING_SHEET

    async def register_sheet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sheet URL/ID input during registration."""
        sheet_input = update.message.text.strip() if update.message.text else ""

        # Extract sheet ID from URL or validate as ID
        sheet_id = extract_sheet_id(sheet_input)
        if not sheet_id:
            await update.message.reply_text(Messages.REGISTER_INVALID_SHEET)
            return AWAITING_SHEET

        # Validate sheet access and create required tabs
        await update.message.reply_text(Messages.REGISTER_PROCESSING)

        try:
            spreadsheet = self.sheets_manager.open_spreadsheet(sheet_id)
            # Pre-create all required worksheets
            self.sheets_manager.ensure_all_worksheets(spreadsheet)
            logger.info(f"Successfully validated and initialized sheet: {sheet_id}")
        except SheetNotFoundError:
            message = Messages.REGISTER_SHEET_NOT_FOUND.format(sheet_id=sheet_id)
            await update.message.reply_text(message)
            await update.message.reply_text(Messages.REGISTER_ASK_SHEET)
            return AWAITING_SHEET
        except (WorksheetNotFoundError, Exception) as e:
            logger.error(f"Error validating sheet {sheet_id}: {str(e)}")
            message = Messages.REGISTER_SHEET_ACCESS_ERROR.format(sheet_id=sheet_id)
            await update.message.reply_text(message)
            await update.message.reply_text(Messages.REGISTER_ASK_SHEET)
            return AWAITING_SHEET

        # Register the tutor
        telegram_id = str(update.effective_user.id)
        name = context.user_data.get("name", "Unknown")

        try:
            self.tutors_db.register_tutor(
                telegram_id=telegram_id, name=name, sheets_id=sheet_id
            )
            message = Messages.REGISTER_SUCCESS.format(name=name, sheet_id=sheet_id)
            await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
            logger.info(f"Tutor registered: {telegram_id} - {name}")
            return ConversationHandler.END
        except TutorAlreadyExistsError:
            message = Messages.REGISTER_DUPLICATE.format(name=name)
            await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
            logger.warning(f"Duplicate registration attempt for {telegram_id}")
            return ConversationHandler.END

    async def register_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cancellation of registration conversation."""
        await update.message.reply_text(
            Messages.REGISTER_CANCELLED, reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command."""
        telegram_id = str(update.effective_user.id)

        try:
            tutor = self.tutors_db.get_tutor(telegram_id)
        except TutorNotFoundError:
            await update.message.reply_text(
                Messages.PROFILE_NOT_REGISTERED, reply_markup=ReplyKeyboardRemove()
            )
            return

        # Format profile information
        created_at = tutor.created_at
        if isinstance(created_at, str):
            try:
                dt = datetime.fromisoformat(created_at)
                created_at = dt.strftime("%d.%m.%Y %H:%M")
            except (ValueError, AttributeError):
                created_at = created_at[:10]  # Just the date part

        updated_at = tutor.updated_at
        if isinstance(updated_at, str):
            try:
                dt = datetime.fromisoformat(updated_at)
                updated_at = dt.strftime("%d.%m.%Y %H:%M")
            except (ValueError, AttributeError):
                updated_at = updated_at[:10]  # Just the date part

        profile_text = (
            f"{Messages.PROFILE_HEADER}\n\n"
            f"{Messages.PROFILE_NAME.format(name=tutor.name)}\n"
            f"{Messages.PROFILE_SHEET.format(sheet_id=tutor.sheets_id)}\n"
            f"{Messages.PROFILE_REGISTERED.format(created_at=created_at)}\n"
            f"{Messages.PROFILE_UPDATED.format(updated_at=updated_at)}\n\n"
            f"{Messages.PROFILE_FOOTER}"
        )

        await update.message.reply_text(profile_text, reply_markup=ReplyKeyboardRemove())
        logger.info(f"Profile viewed by tutor: {telegram_id}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await update.message.reply_text(Messages.HELP_TEXT, reply_markup=ReplyKeyboardRemove())

    def get_conversation_handler(self) -> ConversationHandler:
        """Get the ConversationHandler for registration."""
        return ConversationHandler(
            entry_points=[
                CommandHandler(config.BotCommands.REGISTER.value, self.register_start),
            ],
            states={
                AWAITING_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.register_name),
                    CommandHandler("cancel", self.register_cancel),
                ],
                AWAITING_SHEET: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.register_sheet),
                    CommandHandler("cancel", self.register_cancel),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.register_cancel)],
            allow_reentry=False,
        )


def setup_auth_handlers(
    application, tutors_db: TutorsDB, sheets_manager: SheetsManager
):
    """Set up authentication handlers in the application.

    Args:
        application: The Telegram Application instance.
        tutors_db: TutorsDB instance.
        sheets_manager: SheetsManager instance.
    """
    auth_handlers = AuthHandlers(tutors_db, sheets_manager)

    # Add command handlers
    application.add_handler(
        CommandHandler(config.BotCommands.START.value, auth_handlers.start_command)
    )
    application.add_handler(auth_handlers.get_conversation_handler())
    application.add_handler(
        CommandHandler(config.BotCommands.PROFILE.value, auth_handlers.profile_command)
    )
    application.add_handler(
        CommandHandler(config.BotCommands.HELP.value, auth_handlers.help_command)
    )

    logger.info("Auth handlers set up successfully")
