"""Tests for sheets manager."""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, MagicMock, patch

from database.sheets_manager import SheetsManager, WORKSHEET_HEADERS
from database.exceptions import (
    AuthenticationError,
    SheetNotFoundError,
    WorksheetNotFoundError,
    MalformedDataError,
)
from utils.models import Student, Lesson, Payment


@pytest.fixture
def temp_credentials():
    """Create temporary credentials file."""
    credentials_data = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2a2rwplBCDVx7tqNgXJ9vr6a/PJ8n1qNgLNKNHmSY1L4RzIU\nqKE2K0yA0Z5TbP9B8aQ7W2QX6qz5H8T3W7Q7R8S9T0V9U0W1X2Y3Z4a5B6c7D8e\n9E0F1G2H3I4J5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1a2b3c4d5e6f7g8h9i0\njKlmnoPqrStUvWxYz0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3\nx4y5z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4S5T6U7V8W9X0Y1Z2a3b4c5\nd6e7f8g9h0QIDAQABAoIBAFw2q7LOgzPb6QdzvZDTfzvUlgcCXNOg8kFLF1hKNR7H\nrI9SabEhW1OY0WQ6W3K7N8O9Q9Q9R0R9S0S9T0T0U0U0V0V1W0W1X0X1Y0Y1Z0Z1\na1a2b2b3c3c4d4d5e5e6f6f7g7g8h8h9i9i0j0j1k1k2l2l3m3m4n4n5o5o6p6p7\nq7q8r8r9s9s0t0t1u1u2v2v3w3w4x4x5y5y6z6z7A7A8B8B9C9C0D0D1E1E2F2F3\nG3G4H4H5I5I6J6J7K7K8L8L9M9M0N0N1O1O2P2P3Q3Q4R4R5S5S6T6T7U7U8V8V9\nW9W0X0X1Y1Y2Z2Z3a3a4b4b5c5c6d6d7e7e8f8f9g9g0h0h1i1i2j2j3k3k4l4l5\nm5m6n6n7o7o8p8p9q9q0r0r1s1s2t2t3u3u4v4v5w5w6x6x7y7y8z8z9A9A0B0B1\nC1C2D2D3E3E4F4F5G5G6H6H7I7I8J8J9K9K0L0L1M1M2N2N3O3O4P4P5Q5Q6R6R7\nS7S8T8T9U9U0V0V1W1W2X2X3Y3Y4Z4Z5a5a6b6b7c7c8d8d9e9e0f0f1g1g2h2h3\nAECgYEA0gAaA1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7\nA8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4R5S6T7U8V9W0X1Y2Z3a4b5c6d7e8f9\ng0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9A0B1C2D3E4F5G6H7I8J9K0L1\nM2N3O4P5Q6R7S8T9U0V1W2X3Y4Z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3\ns4t5u6v7w8x9y0z1A2B3C4D5E6F7G8H9I0j1K2L3M4N5O6P7Q8R9S0T1U2V3W4X5\nY6Z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3A4B5C6D7\nE8F9G0H1I2J3K4L5M6N7O8P9Q0CgYEA0gAaA1a2b3c4d5e6f7g8h9i0j1k2l3m4n5\no6p7q8r9s0t1u2v3w4x5y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4R5S6T7\nU8V9W0X1Y2Z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9\nA0B1C2D3E4F5G6H7I8J9K0L1M2N3O4P5Q6R7S8T9U0V1W2X3Y4Z5a6b7c8d9e0f1\ng2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8x9y0z1A2B3C4D5E6F7G8H9I0j1K2L3\nM4N5O6P7Q8R9S0T1U2V3W4X5Y6Z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5\ns6t7u8v9w0x1y2z3A4B5C6D7E8F9G0H1I2J3K4L5M6N7O8P9Q0CgYBj8qKQfxWk\nKkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCk\nCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCk\nCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCk\nCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCk\nCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCkCk\nQKBgG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0g\nG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0g\nG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0g\nG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0g\nG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0g\nG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0gG0g\n-----END RSA PRIVATE KEY-----",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(credentials_data, f)
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestSheetsManager:
    """Test SheetsManager."""

    def test_auth_file_not_found(self):
        """Test authentication error when credentials file not found."""
        with pytest.raises(AuthenticationError):
            SheetsManager("nonexistent.json")

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_initialization(self, mock_creds, mock_auth, temp_credentials):
        """Test manager initialization."""
        mock_creds.return_value = MagicMock()
        mock_auth.return_value = MagicMock()

        manager = SheetsManager(temp_credentials)
        assert manager.client is not None
        mock_creds.assert_called_once()

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_open_spreadsheet(self, mock_creds, mock_auth, temp_credentials):
        """Test opening spreadsheet."""
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = mock_client

        manager = SheetsManager(temp_credentials)
        spreadsheet = manager.open_spreadsheet("sheet-123")

        assert spreadsheet == mock_spreadsheet
        mock_client.open_by_key.assert_called_with("sheet-123")

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_open_spreadsheet_not_found(
        self, mock_creds, mock_auth, temp_credentials
    ):
        """Test opening nonexistent spreadsheet."""
        mock_client = MagicMock()
        mock_client.open_by_key.side_effect = (
            Exception("Spreadsheet not found")
        )

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = mock_client

        manager = SheetsManager(temp_credentials)

        with pytest.raises(SheetNotFoundError):
            manager.open_spreadsheet("nonexistent")

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_ensure_worksheet_exists(
        self, mock_creds, mock_auth, temp_credentials
    ):
        """Test ensuring worksheet exists."""
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = MagicMock()

        manager = SheetsManager(temp_credentials)
        worksheet = manager.ensure_worksheet_exists(
            mock_spreadsheet, "Ученики"
        )

        assert worksheet == mock_worksheet
        mock_spreadsheet.worksheet.assert_called_with("Ученики")

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_ensure_worksheet_create(
        self, mock_creds, mock_auth, temp_credentials
    ):
        """Test creating worksheet when not found."""
        import gspread

        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()

        mock_spreadsheet.worksheet.side_effect = (
            gspread.exceptions.WorksheetNotFound("not found")
        )
        mock_spreadsheet.add_worksheet.return_value = mock_worksheet

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = MagicMock()

        manager = SheetsManager(temp_credentials)
        worksheet = manager.ensure_worksheet_exists(
            mock_spreadsheet, "Ученики"
        )

        assert worksheet == mock_worksheet
        mock_spreadsheet.add_worksheet.assert_called_once()
        mock_worksheet.append_row.assert_called_once()

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_ensure_all_worksheets(
        self, mock_creds, mock_auth, temp_credentials
    ):
        """Test ensuring all worksheets exist."""
        mock_spreadsheet = MagicMock()
        mock_worksheets = {}

        def worksheet_side_effect(name):
            if name not in mock_worksheets:
                ws = MagicMock()
                mock_worksheets[name] = ws
            return mock_worksheets[name]

        mock_spreadsheet.worksheet.side_effect = worksheet_side_effect

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = MagicMock()

        manager = SheetsManager(temp_credentials)
        worksheets = manager.ensure_all_worksheets(mock_spreadsheet)

        assert len(worksheets) == len(WORKSHEET_HEADERS)
        assert "Ученики" in worksheets
        assert "Уроки" in worksheets
        assert "Платежи" in worksheets

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_get_all_students(self, mock_creds, mock_auth, temp_credentials):
        """Test getting all students."""
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ["Имя", "Telegram ID", "Email", "Телефон", "Заметки"],
            ["Alice", "123", "alice@test.com", "+1234567890", "Good"],
            ["Bob", "456", "bob@test.com", "+0987654321", "Great"],
        ]

        mock_spreadsheet.worksheet.return_value = mock_worksheet

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = MagicMock()
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_auth.return_value = mock_client

        manager = SheetsManager(temp_credentials)
        students = manager.get_all_students("sheet-123")

        assert len(students) == 2
        assert students[0].name == "Alice"
        assert students[1].name == "Bob"

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_add_student(self, mock_creds, mock_auth, temp_credentials):
        """Test adding a student."""
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = MagicMock()
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_auth.return_value = mock_client

        manager = SheetsManager(temp_credentials)
        student = Student(name="Charlie", telegram_id="789", email="charlie@test.com")
        manager.add_student("sheet-123", student)

        mock_worksheet.append_row.assert_called_once_with(
            ["Charlie", "789", "charlie@test.com", "", ""]
        )

    @patch("database.sheets_manager.gspread.authorize")
    @patch("database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name")
    def test_log_event(self, mock_creds, mock_auth, temp_credentials):
        """Test logging an event."""
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        mock_creds.return_value = MagicMock()
        mock_auth.return_value = MagicMock()
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_auth.return_value = mock_client

        manager = SheetsManager(temp_credentials)
        manager.log_event("sheet-123", "Student added", "Alice")

        mock_worksheet.append_row.assert_called_once()
        call_args = mock_worksheet.append_row.call_args[0][0]
        assert call_args[1] == "Student added"
        assert call_args[2] == "Alice"
