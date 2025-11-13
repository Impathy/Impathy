"""Tests for tutors database."""

import pytest
import os
import json
import tempfile
from threading import Thread

from database.tutors_db import TutorsDB
from database.exceptions import TutorNotFoundError, TutorAlreadyExistsError
from utils.models import TutorConfig


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestTutorsDB:
    """Test TutorsDB manager."""

    def test_db_initialization(self, temp_db):
        """Test database initialization."""
        db = TutorsDB(temp_db)
        assert os.path.exists(temp_db)

        with open(temp_db) as f:
            data = json.load(f)
        assert "tutors" in data
        assert data["tutors"] == []

    def test_register_tutor(self, temp_db):
        """Test registering a tutor."""
        db = TutorsDB(temp_db)
        config = db.register_tutor("123", "Alice", "sheet-abc")

        assert config.telegram_id == "123"
        assert config.name == "Alice"
        assert config.sheets_id == "sheet-abc"
        assert config.created_at is not None

    def test_register_duplicate_tutor(self, temp_db):
        """Test registering duplicate tutor raises error."""
        db = TutorsDB(temp_db)
        db.register_tutor("123", "Alice", "sheet-abc")

        with pytest.raises(TutorAlreadyExistsError):
            db.register_tutor("123", "Alice2", "sheet-def")

    def test_get_tutor(self, temp_db):
        """Test getting a tutor."""
        db = TutorsDB(temp_db)
        db.register_tutor("456", "Bob", "sheet-xyz")

        config = db.get_tutor("456")
        assert config.name == "Bob"
        assert config.sheets_id == "sheet-xyz"

    def test_get_nonexistent_tutor(self, temp_db):
        """Test getting nonexistent tutor raises error."""
        db = TutorsDB(temp_db)

        with pytest.raises(TutorNotFoundError):
            db.get_tutor("999")

    def test_update_tutor(self, temp_db):
        """Test updating tutor."""
        db = TutorsDB(temp_db)
        db.register_tutor("789", "Charlie", "sheet-123")

        updated = db.update_tutor("789", name="Charlie Updated", sheets_id="sheet-456")
        assert updated.name == "Charlie Updated"
        assert updated.sheets_id == "sheet-456"

        retrieved = db.get_tutor("789")
        assert retrieved.name == "Charlie Updated"

    def test_update_nonexistent_tutor(self, temp_db):
        """Test updating nonexistent tutor raises error."""
        db = TutorsDB(temp_db)

        with pytest.raises(TutorNotFoundError):
            db.update_tutor("999", name="Nobody")

    def test_delete_tutor(self, temp_db):
        """Test deleting a tutor."""
        db = TutorsDB(temp_db)
        db.register_tutor("111", "David", "sheet-aaa")

        db.delete_tutor("111")

        with pytest.raises(TutorNotFoundError):
            db.get_tutor("111")

    def test_delete_nonexistent_tutor(self, temp_db):
        """Test deleting nonexistent tutor raises error."""
        db = TutorsDB(temp_db)

        with pytest.raises(TutorNotFoundError):
            db.delete_tutor("999")

    def test_list_tutors(self, temp_db):
        """Test listing all tutors."""
        db = TutorsDB(temp_db)
        db.register_tutor("111", "Alice", "sheet-1")
        db.register_tutor("222", "Bob", "sheet-2")
        db.register_tutor("333", "Charlie", "sheet-3")

        tutors = db.list_tutors()
        assert len(tutors) == 3
        names = [t.name for t in tutors]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names

    def test_tutor_exists(self, temp_db):
        """Test checking if tutor exists."""
        db = TutorsDB(temp_db)
        db.register_tutor("444", "Eve", "sheet-e")

        assert db.tutor_exists("444") is True
        assert db.tutor_exists("999") is False

    def test_thread_safe_operations(self, temp_db):
        """Test thread-safe operations."""
        db = TutorsDB(temp_db)
        results = []

        def register_tutors():
            for i in range(10):
                try:
                    db.register_tutor(f"tutor-{i}", f"Tutor {i}", f"sheet-{i}")
                    results.append("success")
                except Exception as e:
                    results.append(f"error: {e}")

        threads = [Thread(target=register_tutors) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        tutors = db.list_tutors()
        assert len(tutors) >= 10

    def test_persistence(self, temp_db):
        """Test data persistence across instances."""
        db1 = TutorsDB(temp_db)
        db1.register_tutor("555", "Frank", "sheet-f")

        db2 = TutorsDB(temp_db)
        config = db2.get_tutor("555")
        assert config.name == "Frank"

    def test_empty_db_initialization(self, temp_db):
        """Test initializing empty database."""
        # Remove the file to test empty initialization
        os.unlink(temp_db)

        db = TutorsDB(temp_db)
        assert os.path.exists(temp_db)

        tutors = db.list_tutors()
        assert len(tutors) == 0
