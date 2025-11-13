"""Integration tests demonstrating complete workflow."""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch

from database.sheets_manager import SheetsManager
from database.tutors_db import TutorsDB
from utils.models import Student, Lesson, Payment
from database.exceptions import TutorNotFoundError


@pytest.fixture
def temp_db():
    """Create temporary database."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_credentials():
    """Create temporary credentials file."""
    import json

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
        import json

        json.dump(credentials_data, f)
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestCompleteWorkflow:
    """Integration tests for complete workflow."""

    def test_register_and_lookup_tutor(self, temp_db):
        """Test registering a tutor and retrieving it."""
        db = TutorsDB(temp_db)

        config = db.register_tutor("123", "Alice", "sheet-123")
        assert config.telegram_id == "123"
        assert config.name == "Alice"
        assert config.sheets_id == "sheet-123"

        retrieved = db.get_tutor("123")
        assert retrieved.name == "Alice"
        assert retrieved.sheets_id == "sheet-123"

    def test_tutor_persistence_across_instances(self, temp_db):
        """Test that tutor data persists across DB instances."""
        db1 = TutorsDB(temp_db)
        db1.register_tutor("456", "Bob", "sheet-456")

        db2 = TutorsDB(temp_db)
        config = db2.get_tutor("456")
        assert config.name == "Bob"

    def test_student_data_conversion(self):
        """Test converting student data to/from rows."""
        original = Student(
            name="Charlie",
            telegram_id="789",
            email="charlie@example.com",
            phone="+1234567890",
            notes="Good student",
        )

        row = original.to_row()
        restored = Student.from_row(row, sheet_row=5)

        assert restored.name == original.name
        assert restored.telegram_id == original.telegram_id
        assert restored.email == original.email
        assert restored.phone == original.phone
        assert restored.notes == original.notes

    def test_lesson_data_conversion(self):
        """Test converting lesson data to/from rows."""
        original = Lesson(
            student_name="David",
            date="2024-01-15",
            time="15:30",
            duration="60",
            topic="Math",
            notes="Good progress",
        )

        row = original.to_row()
        restored = Lesson.from_row(row, sheet_row=3)

        assert restored.student_name == original.student_name
        assert restored.date == original.date
        assert restored.time == original.time
        assert restored.duration == original.duration
        assert restored.topic == original.topic
        assert restored.notes == original.notes

    def test_payment_data_conversion(self):
        """Test converting payment data to/from rows."""
        original = Payment(
            student_name="Eve",
            amount="1000",
            date="2024-01-15",
            method="Card",
            notes="Monthly",
        )

        row = original.to_row()
        restored = Payment.from_row(row, sheet_row=2)

        assert restored.student_name == original.student_name
        assert restored.amount == original.amount
        assert restored.date == original.date
        assert restored.method == original.method
        assert restored.notes == original.notes

    @patch("database.sheets_manager.gspread.authorize")
    @patch(
        "database.sheets_manager.ServiceAccountCredentials.from_json_keyfile_name"
    )
    def test_sheets_manager_workflow(
        self, mock_creds, mock_auth, temp_credentials
    ):
        """Test complete sheets manager workflow."""
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

    def test_multiple_tutor_registrations(self, temp_db):
        """Test registering multiple tutors."""
        db = TutorsDB(temp_db)

        tutors = [
            ("111", "Alice", "sheet-1"),
            ("222", "Bob", "sheet-2"),
            ("333", "Charlie", "sheet-3"),
        ]

        for tid, name, sheet in tutors:
            db.register_tutor(tid, name, sheet)

        all_tutors = db.list_tutors()
        assert len(all_tutors) == 3

        for tid in ["111", "222", "333"]:
            config = db.get_tutor(tid)
            assert config is not None

    def test_duplicate_tutor_registration_fails(self, temp_db):
        """Test that registering duplicate tutor fails."""
        db = TutorsDB(temp_db)
        db.register_tutor("444", "David", "sheet-4")

        with pytest.raises(Exception):
            db.register_tutor("444", "David2", "sheet-5")

    def test_missing_tutor_raises_error(self, temp_db):
        """Test that looking up missing tutor raises error."""
        db = TutorsDB(temp_db)

        with pytest.raises(TutorNotFoundError):
            db.get_tutor("nonexistent")
