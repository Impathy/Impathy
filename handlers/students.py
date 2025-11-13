"""Student management handlers for the Telegram bot."""

import logging
from typing import Optional

from telegram import Update, ReplyKeyboardRemove
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
    TutorNotFoundError,
    SheetNotFoundError,
    WorksheetNotFoundError,
    MalformedDataError,
)
from utils.messages import Messages
from utils.validators import sanitize_name

logger = logging.getLogger(__name__)

# Conversation states for add_student
ADD_AWAITING_PARENT, ADD_AWAITING_STUDENT, ADD_AWAITING_COST = range(3)

# Conversation states for delete_student
DEL_AWAITING_PARENT, DEL_AWAITING_STUDENT, DEL_AWAITING_CONFIRM = range(3, 6)


class StudentHandlers:
    """Handlers for student management commands."""

    def __init__(self, tutors_db: TutorsDB, sheets_manager: SheetsManager):
        """Initialize student handlers.

        Args:
            tutors_db: TutorsDB instance for managing tutor configurations.
            sheets_manager: SheetsManager instance for managing Google Sheets.
        """
        self.tutors_db = tutors_db
        self.sheets_manager = sheets_manager

    async def _check_registration(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> Optional[str]:
        """Check if user is registered and return sheets_id.

        Returns:
            sheets_id if registered, None otherwise.
        """
        telegram_id = str(update.effective_user.id)
        try:
            tutor = self.tutors_db.get_tutor(telegram_id)
            return tutor.sheets_id
        except TutorNotFoundError:
            await update.message.reply_text(
                Messages.PROFILE_NOT_REGISTERED, reply_markup=ReplyKeyboardRemove()
            )
            return None

    async def add_student_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the add student conversation."""
        sheets_id = await self._check_registration(update, context)
        if not sheets_id:
            return ConversationHandler.END

        # Check if args are provided
        if context.args and len(context.args) >= 3:
            # All arguments provided: /add_student Parent Student Cost
            parent_name = sanitize_name(" ".join(context.args[:-2]))
            student_name = sanitize_name(context.args[-2])
            lesson_cost = context.args[-1]

            try:
                self.sheets_manager.add_student_record(
                    sheets_id, parent_name, student_name, lesson_cost
                )
                message = Messages.ADD_STUDENT_SUCCESS.format(
                    parent_name=parent_name,
                    student_name=student_name,
                    lesson_cost=lesson_cost,
                )
                await update.message.reply_text(
                    message, reply_markup=ReplyKeyboardRemove()
                )
                logger.info(f"Student added: {parent_name} - {student_name}")
                return ConversationHandler.END
            except ValueError as e:
                await update.message.reply_text(
                    Messages.ADD_STUDENT_DUPLICATE.format(
                        parent_name=parent_name, student_name=student_name
                    )
                )
                logger.warning(f"Duplicate student: {parent_name} - {student_name}")
                return ConversationHandler.END
            except (SheetNotFoundError, WorksheetNotFoundError, Exception) as e:
                logger.error(f"Error adding student: {str(e)}")
                await update.message.reply_text(
                    Messages.format_error(str(e)), reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END

        # Interactive mode - no args provided
        context.user_data["sheets_id"] = sheets_id
        await update.message.reply_text(
            Messages.ADD_STUDENT_PROMPT_PARENT, reply_markup=ReplyKeyboardRemove()
        )
        return ADD_AWAITING_PARENT

    async def add_student_parent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle parent name input."""
        parent_name = sanitize_name(update.message.text.strip()) if update.message.text else ""

        if not parent_name:
            await update.message.reply_text(Messages.ERROR_INVALID_INPUT)
            await update.message.reply_text(Messages.ADD_STUDENT_PROMPT_PARENT)
            return ADD_AWAITING_PARENT

        context.user_data["parent_name"] = parent_name
        await update.message.reply_text(Messages.ADD_STUDENT_PROMPT_STUDENT)
        return ADD_AWAITING_STUDENT

    async def add_student_student(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle student name input."""
        student_name = sanitize_name(update.message.text.strip()) if update.message.text else ""

        if not student_name:
            await update.message.reply_text(Messages.ERROR_INVALID_INPUT)
            await update.message.reply_text(Messages.ADD_STUDENT_PROMPT_STUDENT)
            return ADD_AWAITING_STUDENT

        context.user_data["student_name"] = student_name
        await update.message.reply_text(Messages.ADD_STUDENT_PROMPT_COST)
        return ADD_AWAITING_COST

    async def add_student_cost(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle lesson cost input and save the student."""
        lesson_cost = update.message.text.strip() if update.message.text else ""

        if not lesson_cost:
            await update.message.reply_text(Messages.ERROR_INVALID_INPUT)
            await update.message.reply_text(Messages.ADD_STUDENT_PROMPT_COST)
            return ADD_AWAITING_COST

        sheets_id = context.user_data.get("sheets_id")
        parent_name = context.user_data.get("parent_name", "")
        student_name = context.user_data.get("student_name", "")

        try:
            self.sheets_manager.add_student_record(
                sheets_id, parent_name, student_name, lesson_cost
            )
            message = Messages.ADD_STUDENT_SUCCESS.format(
                parent_name=parent_name,
                student_name=student_name,
                lesson_cost=lesson_cost,
            )
            await update.message.reply_text(
                message, reply_markup=ReplyKeyboardRemove()
            )
            logger.info(f"Student added: {parent_name} - {student_name}")
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text(
                Messages.ADD_STUDENT_DUPLICATE.format(
                    parent_name=parent_name, student_name=student_name
                ),
                reply_markup=ReplyKeyboardRemove(),
            )
            logger.warning(f"Duplicate student: {parent_name} - {student_name}")
            return ConversationHandler.END
        except (SheetNotFoundError, WorksheetNotFoundError, Exception) as e:
            logger.error(f"Error adding student: {str(e)}")
            await update.message.reply_text(
                Messages.format_error(str(e)), reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

    async def add_student_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cancellation of add student conversation."""
        await update.message.reply_text(
            Messages.ADD_STUDENT_CANCELLED, reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def list_students_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list_students command."""
        sheets_id = await self._check_registration(update, context)
        if not sheets_id:
            return

        try:
            records = self.sheets_manager.get_student_records(sheets_id)

            if not records:
                await update.message.reply_text(
                    Messages.LIST_STUDENTS_EMPTY, reply_markup=ReplyKeyboardRemove()
                )
                return

            message = Messages.LIST_STUDENTS_HEADER
            for idx, record in enumerate(records, start=1):
                message += Messages.LIST_STUDENTS_ITEM.format(
                    idx=idx,
                    parent_name=record.parent_name,
                    student_name=record.student_name,
                    lesson_cost=record.lesson_cost,
                )
                message += "\n"

            await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
            logger.info(f"Listed {len(records)} students")
        except (SheetNotFoundError, WorksheetNotFoundError, MalformedDataError) as e:
            logger.error(f"Error listing students: {str(e)}")
            await update.message.reply_text(
                Messages.format_error(str(e)), reply_markup=ReplyKeyboardRemove()
            )

    async def delete_student_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the delete student conversation."""
        sheets_id = await self._check_registration(update, context)
        if not sheets_id:
            return ConversationHandler.END

        # Check if args are provided
        if context.args and len(context.args) >= 2:
            # All arguments provided: /delete_student Parent Student
            parent_name = sanitize_name(" ".join(context.args[:-1]))
            student_name = sanitize_name(context.args[-1])

            try:
                deleted = self.sheets_manager.delete_student_record(
                    sheets_id, parent_name, student_name
                )
                if deleted:
                    message = Messages.DELETE_STUDENT_SUCCESS.format(
                        parent_name=parent_name, student_name=student_name
                    )
                    await update.message.reply_text(
                        message, reply_markup=ReplyKeyboardRemove()
                    )
                    logger.info(f"Student deleted: {parent_name} - {student_name}")
                else:
                    await update.message.reply_text(
                        Messages.DELETE_STUDENT_NOT_FOUND.format(
                            parent_name=parent_name, student_name=student_name
                        ),
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    logger.warning(f"Student not found: {parent_name} - {student_name}")
                return ConversationHandler.END
            except (SheetNotFoundError, WorksheetNotFoundError, Exception) as e:
                logger.error(f"Error deleting student: {str(e)}")
                await update.message.reply_text(
                    Messages.format_error(str(e)), reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END

        # Interactive mode - no args provided
        context.user_data["sheets_id"] = sheets_id
        await update.message.reply_text(
            Messages.DELETE_STUDENT_PROMPT_PARENT, reply_markup=ReplyKeyboardRemove()
        )
        return DEL_AWAITING_PARENT

    async def delete_student_parent(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle parent name input for deletion."""
        parent_name = sanitize_name(update.message.text.strip()) if update.message.text else ""

        if not parent_name:
            await update.message.reply_text(Messages.ERROR_INVALID_INPUT)
            await update.message.reply_text(Messages.DELETE_STUDENT_PROMPT_PARENT)
            return DEL_AWAITING_PARENT

        context.user_data["parent_name"] = parent_name
        await update.message.reply_text(Messages.DELETE_STUDENT_PROMPT_STUDENT)
        return DEL_AWAITING_STUDENT

    async def delete_student_student(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle student name input for deletion."""
        student_name = sanitize_name(update.message.text.strip()) if update.message.text else ""

        if not student_name:
            await update.message.reply_text(Messages.ERROR_INVALID_INPUT)
            await update.message.reply_text(Messages.DELETE_STUDENT_PROMPT_STUDENT)
            return DEL_AWAITING_STUDENT

        parent_name = context.user_data.get("parent_name", "")
        context.user_data["student_name"] = student_name

        message = Messages.DELETE_STUDENT_CONFIRMATION.format(
            parent_name=parent_name, student_name=student_name
        )
        await update.message.reply_text(message)
        return DEL_AWAITING_CONFIRM

    async def delete_student_confirm(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle deletion confirmation."""
        user_input = update.message.text.strip().lower()

        if user_input.startswith("/confirm"):
            sheets_id = context.user_data.get("sheets_id")
            parent_name = context.user_data.get("parent_name", "")
            student_name = context.user_data.get("student_name", "")

            try:
                deleted = self.sheets_manager.delete_student_record(
                    sheets_id, parent_name, student_name
                )
                if deleted:
                    message = Messages.DELETE_STUDENT_SUCCESS.format(
                        parent_name=parent_name, student_name=student_name
                    )
                    await update.message.reply_text(
                        message, reply_markup=ReplyKeyboardRemove()
                    )
                    logger.info(f"Student deleted: {parent_name} - {student_name}")
                    return ConversationHandler.END
                else:
                    await update.message.reply_text(
                        Messages.DELETE_STUDENT_NOT_FOUND.format(
                            parent_name=parent_name, student_name=student_name
                        ),
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    logger.warning(f"Student not found: {parent_name} - {student_name}")
                    return ConversationHandler.END
            except (SheetNotFoundError, WorksheetNotFoundError, Exception) as e:
                logger.error(f"Error deleting student: {str(e)}")
                await update.message.reply_text(
                    Messages.format_error(str(e)), reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END
        elif user_input.startswith("/cancel"):
            await update.message.reply_text(
                Messages.DELETE_STUDENT_CANCELLED, reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                Messages.DELETE_STUDENT_CONFIRMATION.format(
                    parent_name=context.user_data.get("parent_name", ""),
                    student_name=context.user_data.get("student_name", ""),
                )
            )
            return DEL_AWAITING_CONFIRM

    async def delete_student_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cancellation of delete student conversation."""
        await update.message.reply_text(
            Messages.DELETE_STUDENT_CANCELLED, reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def get_add_student_handler(self) -> ConversationHandler:
        """Get the ConversationHandler for adding students."""
        return ConversationHandler(
            entry_points=[
                CommandHandler(config.BotCommands.ADD_STUDENT.value, self.add_student_start),
            ],
            states={
                ADD_AWAITING_PARENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_student_parent),
                    CommandHandler("cancel", self.add_student_cancel),
                ],
                ADD_AWAITING_STUDENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_student_student),
                    CommandHandler("cancel", self.add_student_cancel),
                ],
                ADD_AWAITING_COST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_student_cost),
                    CommandHandler("cancel", self.add_student_cancel),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.add_student_cancel)],
            allow_reentry=False,
        )

    def get_delete_student_handler(self) -> ConversationHandler:
        """Get the ConversationHandler for deleting students."""
        return ConversationHandler(
            entry_points=[
                CommandHandler(config.BotCommands.DELETE_STUDENT.value, self.delete_student_start),
            ],
            states={
                DEL_AWAITING_PARENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.delete_student_parent),
                    CommandHandler("cancel", self.delete_student_cancel),
                ],
                DEL_AWAITING_STUDENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.delete_student_student),
                    CommandHandler("cancel", self.delete_student_cancel),
                ],
                DEL_AWAITING_CONFIRM: [
                    CommandHandler("confirm", self.delete_student_confirm),
                    CommandHandler("cancel", self.delete_student_cancel),
                    MessageHandler(filters.TEXT, self.delete_student_confirm),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.delete_student_cancel)],
            allow_reentry=False,
        )


def setup_student_handlers(application, tutors_db: TutorsDB, sheets_manager: SheetsManager):
    """Set up student handlers in the application.

    Args:
        application: The Telegram Application instance.
        tutors_db: TutorsDB instance.
        sheets_manager: SheetsManager instance.
    """
    student_handlers = StudentHandlers(tutors_db, sheets_manager)

    # Add conversation handlers
    application.add_handler(student_handlers.get_add_student_handler())
    application.add_handler(student_handlers.get_delete_student_handler())

    # Add list command handler
    application.add_handler(
        CommandHandler(config.BotCommands.LIST_STUDENTS.value, student_handlers.list_students_command)
    )

    logger.info("Student handlers set up successfully")
