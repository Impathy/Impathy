"""Tests for authentication handlers."""

import pytest
import tempfile
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from handlers.auth import AuthHandlers, AWAITING_NAME, AWAITING_SHEET
from database.tutors_db import TutorsDB
from database.sheets_manager import SheetsManager
from database.exceptions import (
    TutorAlreadyExistsError,
    TutorNotFoundError,
    SheetNotFoundError,
    WorksheetNotFoundError,
)
from utils.validators import extract_sheet_id, validate_name, sanitize_name


class TestExtractSheetId:
    """Tests for sheet ID extraction."""

    def test_extract_from_full_url(self):
        """Test extracting sheet ID from full Google Sheets URL."""
        url = "https://docs.google.com/spreadsheets/d/1ABC2DEF3GHI/edit"
        assert extract_sheet_id(url) == "1ABC2DEF3GHI"

    def test_extract_from_url_with_extra_params(self):
        """Test extracting sheet ID from URL with query parameters."""
        url = "https://docs.google.com/spreadsheets/d/1ABC2DEF3GHI/edit?usp=sharing"
        assert extract_sheet_id(url) == "1ABC2DEF3GHI"

    def test_direct_sheet_id(self):
        """Test that direct sheet ID is recognized."""
        sheet_id = "1ABC2DEF3GHI4JKL5MNO"
        assert extract_sheet_id(sheet_id) == sheet_id

    def test_invalid_short_id(self):
        """Test that short IDs are rejected."""
        assert extract_sheet_id("ABC") is None

    def test_invalid_url(self):
        """Test that invalid URLs are rejected."""
        assert extract_sheet_id("https://example.com") is None

    def test_empty_string(self):
        """Test that empty strings are rejected."""
        assert extract_sheet_id("") is None

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        url = "  https://docs.google.com/spreadsheets/d/1ABC2DEF3GHI/edit  "
        assert extract_sheet_id(url) == "1ABC2DEF3GHI"


class TestValidateName:
    """Tests for name validation."""

    def test_valid_english_name(self):
        """Test that valid English names are accepted."""
        assert validate_name("John Doe") is True

    def test_valid_russian_name(self):
        """Test that valid Russian names are accepted."""
        assert validate_name("Иван Петров") is True

    def test_valid_name_with_hyphen(self):
        """Test that names with hyphens are accepted."""
        assert validate_name("Mary-Jane") is True

    def test_valid_name_with_apostrophe(self):
        """Test that names with apostrophes are accepted."""
        assert validate_name("O'Brien") is True

    def test_too_short_name(self):
        """Test that very short names are rejected."""
        assert validate_name("A") is False

    def test_empty_name(self):
        """Test that empty names are rejected."""
        assert validate_name("") is False

    def test_whitespace_only_name(self):
        """Test that whitespace-only names are rejected."""
        assert validate_name("   ") is False

    def test_too_long_name(self):
        """Test that very long names are rejected."""
        long_name = "A" * 101
        assert validate_name(long_name) is False

    def test_name_with_numbers(self):
        """Test that names with numbers are accepted."""
        assert validate_name("Agent 47") is True

    def test_name_with_invalid_characters(self):
        """Test that names with invalid special characters are rejected."""
        assert validate_name("John@Doe") is False


class TestSanitizeName:
    """Tests for name sanitization."""

    def test_strip_leading_trailing_whitespace(self):
        """Test that leading and trailing whitespace is removed."""
        assert sanitize_name("  John Doe  ") == "John Doe"

    def test_remove_extra_internal_whitespace(self):
        """Test that extra internal whitespace is removed."""
        assert sanitize_name("John    Doe") == "John Doe"

    def test_preserve_normal_spacing(self):
        """Test that normal spacing is preserved."""
        assert sanitize_name("John Doe") == "John Doe"


class TestAuthHandlers:
    """Tests for authentication handlers."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"tutors": []}, f)
            return f.name

    @pytest.fixture
    def tutors_db(self, temp_db_path):
        """Create a TutorsDB instance."""
        return TutorsDB(temp_db_path)

    @pytest.fixture
    def sheets_manager(self):
        """Create a mock SheetsManager."""
        manager = MagicMock(spec=SheetsManager)
        return manager

    @pytest.fixture
    def auth_handlers(self, tutors_db, sheets_manager):
        """Create AuthHandlers instance."""
        return AuthHandlers(tutors_db, sheets_manager)

    @pytest.fixture
    def mock_update(self):
        """Create a mock Update object."""
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456789
        update.message = Mock(spec=Message)
        return update

    @pytest.fixture
    def mock_context(self):
        """Create a mock ContextTypes."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_start_new_user(self, auth_handlers, mock_update, mock_context):
        """Test /start command for new users."""
        mock_update.message.reply_text = AsyncMock()
        
        await auth_handlers.start_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]
        assert "👋 Добро пожаловать" in message

    @pytest.mark.asyncio
    async def test_start_registered_user(self, auth_handlers, tutors_db, mock_update, mock_context):
        """Test /start command for registered users."""
        # Register the user first
        tutors_db.register_tutor("123456789", "John Doe", "1ABC2DEF")
        
        mock_update.message.reply_text = AsyncMock()
        
        await auth_handlers.start_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]
        assert "John Doe" in message

    @pytest.mark.asyncio
    async def test_register_start_new_user(self, auth_handlers, mock_update, mock_context):
        """Test /register command start for new users."""
        mock_update.message.reply_text = AsyncMock()
        
        result = await auth_handlers.register_start(mock_update, mock_context)
        
        assert result == AWAITING_NAME
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_start_already_registered(self, auth_handlers, tutors_db, mock_update, mock_context):
        """Test /register command start for already registered users."""
        tutors_db.register_tutor("123456789", "John Doe", "1ABC2DEF")
        
        mock_update.message.reply_text = AsyncMock()
        
        result = await auth_handlers.register_start(mock_update, mock_context)
        
        assert result == -1  # ConversationHandler.END

    @pytest.mark.asyncio
    async def test_register_name_valid(self, auth_handlers, mock_update, mock_context):
        """Test name input during registration."""
        mock_update.message.text = "John Doe"
        mock_update.message.reply_text = AsyncMock()
        
        result = await auth_handlers.register_name(mock_update, mock_context)
        
        assert result == AWAITING_SHEET
        assert mock_context.user_data["name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_register_name_invalid(self, auth_handlers, mock_update, mock_context):
        """Test invalid name input during registration."""
        mock_update.message.text = "A"  # Too short
        mock_update.message.reply_text = AsyncMock()
        
        result = await auth_handlers.register_name(mock_update, mock_context)
        
        assert result == AWAITING_NAME
        mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_register_sheet_valid(self, auth_handlers, sheets_manager, mock_update, mock_context):
        """Test valid sheet URL/ID during registration."""
        mock_update.message.text = "1ABC2DEF3GHI4JKL"
        mock_update.message.reply_text = AsyncMock()
        mock_context.user_data["name"] = "John Doe"
        
        # Mock the sheets manager
        mock_spreadsheet = MagicMock()
        sheets_manager.open_spreadsheet.return_value = mock_spreadsheet
        sheets_manager.ensure_all_worksheets.return_value = {}
        
        result = await auth_handlers.register_sheet(mock_update, mock_context)
        
        assert result == -1  # ConversationHandler.END
        sheets_manager.open_spreadsheet.assert_called_once_with("1ABC2DEF3GHI4JKL")

    @pytest.mark.asyncio
    async def test_register_sheet_invalid_format(self, auth_handlers, mock_update, mock_context):
        """Test invalid sheet URL/ID format."""
        mock_update.message.text = "invalid"
        mock_update.message.reply_text = AsyncMock()
        mock_context.user_data["name"] = "John Doe"
        
        result = await auth_handlers.register_sheet(mock_update, mock_context)
        
        assert result == AWAITING_SHEET
        mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_register_sheet_not_found(self, auth_handlers, sheets_manager, mock_update, mock_context):
        """Test sheet not found error."""
        mock_update.message.text = "1ABC2DEF3GHI4JKL"
        mock_update.message.reply_text = AsyncMock()
        mock_context.user_data["name"] = "John Doe"
        
        sheets_manager.open_spreadsheet.side_effect = SheetNotFoundError("Sheet not found")
        
        result = await auth_handlers.register_sheet(mock_update, mock_context)
        
        assert result == AWAITING_SHEET
        assert sheets_manager.open_spreadsheet.called

    @pytest.mark.asyncio
    async def test_profile_registered_user(self, auth_handlers, tutors_db, mock_update, mock_context):
        """Test /profile command for registered user."""
        tutors_db.register_tutor("123456789", "John Doe", "1ABC2DEF")
        
        mock_update.message.reply_text = AsyncMock()
        
        await auth_handlers.profile_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]
        assert "John Doe" in message
        assert "1ABC2DEF" in message

    @pytest.mark.asyncio
    async def test_profile_unregistered_user(self, auth_handlers, mock_update, mock_context):
        """Test /profile command for unregistered user."""
        mock_update.message.reply_text = AsyncMock()
        
        await auth_handlers.profile_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]
        assert "не зарегистрированы" in message or "not registered" in message.lower()

    @pytest.mark.asyncio
    async def test_help_command(self, auth_handlers, mock_update, mock_context):
        """Test /help command."""
        mock_update.message.reply_text = AsyncMock()
        
        await auth_handlers.help_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]
        assert "/start" in message or "start" in message

    def test_get_conversation_handler(self, auth_handlers):
        """Test that ConversationHandler is properly configured."""
        conv_handler = auth_handlers.get_conversation_handler()
        assert conv_handler is not None
        assert conv_handler.entry_points
        assert conv_handler.states
        assert AWAITING_NAME in conv_handler.states
        assert AWAITING_SHEET in conv_handler.states
