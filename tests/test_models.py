"""Tests for data models."""

import pytest
from utils.models import Student, Lesson, Payment, TutorConfig


class TestStudent:
    """Test Student model."""

    def test_student_creation(self):
        """Test student creation."""
        student = Student(name="Alice", telegram_id="123", email="alice@example.com")
        assert student.name == "Alice"
        assert student.telegram_id == "123"
        assert student.email == "alice@example.com"

    def test_student_to_row(self):
        """Test converting student to row."""
        student = Student(
            name="Bob",
            telegram_id="456",
            email="bob@example.com",
            phone="+1234567890",
            notes="Good student",
        )
        row = student.to_row()
        assert row == ["Bob", "456", "bob@example.com", "+1234567890", "Good student"]

    def test_student_to_row_optional_fields(self):
        """Test converting student with optional fields to row."""
        student = Student(name="Charlie")
        row = student.to_row()
        assert row == ["Charlie", "", "", "", ""]

    def test_student_from_row(self):
        """Test creating student from row."""
        row = ["David", "789", "david@example.com", "+9876543210", "Notes"]
        student = Student.from_row(row, sheet_row=5)
        assert student.name == "David"
        assert student.telegram_id == "789"
        assert student.email == "david@example.com"
        assert student.phone == "+9876543210"
        assert student.notes == "Notes"
        assert student.sheet_row == 5

    def test_student_from_row_partial(self):
        """Test creating student from partial row."""
        row = ["Eve"]
        student = Student.from_row(row)
        assert student.name == "Eve"
        assert student.telegram_id is None
        assert student.email is None

    def test_student_to_dict(self):
        """Test converting student to dict."""
        student = Student(name="Frank", telegram_id="999")
        data = student.to_dict()
        assert data["name"] == "Frank"
        assert data["telegram_id"] == "999"


class TestLesson:
    """Test Lesson model."""

    def test_lesson_creation(self):
        """Test lesson creation."""
        lesson = Lesson(
            student_name="Alice", date="2024-01-15", time="10:00", duration="60"
        )
        assert lesson.student_name == "Alice"
        assert lesson.date == "2024-01-15"

    def test_lesson_to_row(self):
        """Test converting lesson to row."""
        lesson = Lesson(
            student_name="Bob",
            date="2024-01-16",
            time="14:30",
            duration="45",
            topic="Math",
            notes="Good progress",
        )
        row = lesson.to_row()
        assert row == ["Bob", "2024-01-16", "14:30", "45", "Math", "Good progress"]

    def test_lesson_from_row(self):
        """Test creating lesson from row."""
        row = ["Charlie", "2024-01-17", "09:00", "90", "Physics", "Review"]
        lesson = Lesson.from_row(row, sheet_row=10)
        assert lesson.student_name == "Charlie"
        assert lesson.date == "2024-01-17"
        assert lesson.time == "09:00"
        assert lesson.sheet_row == 10


class TestPayment:
    """Test Payment model."""

    def test_payment_creation(self):
        """Test payment creation."""
        payment = Payment(student_name="Alice", amount="100", date="2024-01-15")
        assert payment.student_name == "Alice"
        assert payment.amount == "100"
        assert payment.date == "2024-01-15"

    def test_payment_to_row(self):
        """Test converting payment to row."""
        payment = Payment(
            student_name="Bob",
            amount="150",
            date="2024-01-16",
            method="Cash",
            notes="Paid in advance",
        )
        row = payment.to_row()
        assert row == ["Bob", "150", "2024-01-16", "Cash", "Paid in advance"]

    def test_payment_from_row(self):
        """Test creating payment from row."""
        row = ["Charlie", "200", "2024-01-17", "Bank Transfer", "Monthly"]
        payment = Payment.from_row(row, sheet_row=3)
        assert payment.student_name == "Charlie"
        assert payment.amount == "200"
        assert payment.date == "2024-01-17"
        assert payment.sheet_row == 3


class TestTutorConfig:
    """Test TutorConfig model."""

    def test_tutor_config_creation(self):
        """Test tutor config creation."""
        config = TutorConfig(
            telegram_id="12345", name="John", sheets_id="sheet-123"
        )
        assert config.telegram_id == "12345"
        assert config.name == "John"
        assert config.sheets_id == "sheet-123"

    def test_tutor_config_to_dict(self):
        """Test converting tutor config to dict."""
        config = TutorConfig(
            telegram_id="12345", name="Jane", sheets_id="sheet-456"
        )
        data = config.to_dict()
        assert data["telegram_id"] == "12345"
        assert data["name"] == "Jane"
        assert data["sheets_id"] == "sheet-456"

    def test_tutor_config_from_dict(self):
        """Test creating tutor config from dict."""
        data = {
            "telegram_id": "67890",
            "name": "Jack",
            "sheets_id": "sheet-789",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
        }
        config = TutorConfig.from_dict(data)
        assert config.telegram_id == "67890"
        assert config.name == "Jack"
        assert config.created_at == "2024-01-01T00:00:00"
