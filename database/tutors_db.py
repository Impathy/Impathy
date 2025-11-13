"""Database manager for tutor configurations."""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from threading import Lock
from datetime import datetime

from .exceptions import TutorNotFoundError, TutorAlreadyExistsError, ConfigurationError
from utils.models import TutorConfig


class TutorsDB:
    """Thread-safe manager for tutors configuration."""

    def __init__(self, db_path: str = "tutors_config.json"):
        """Initialize tutors database.

        Args:
            db_path: Path to tutors_config.json file.
        """
        self.db_path = db_path
        self._lock = Lock()
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure database file exists with proper structure."""
        if not os.path.exists(self.db_path):
            self._write_db({"tutors": []})
        else:
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        self._write_db({"tutors": []})
            except IOError:
                self._write_db({"tutors": []})

    def _read_db(self) -> Dict[str, Any]:
        """Read database file with thread safety.

        Returns:
            Database dictionary.

        Raises:
            ConfigurationError: If database file is invalid.
        """
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "tutors" not in data:
                data["tutors"] = []
            return data
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {self.db_path}: {str(e)}")
        except IOError as e:
            raise ConfigurationError(f"Failed to read {self.db_path}: {str(e)}")

    def _write_db(self, data: Dict[str, Any]) -> None:
        """Write database file with thread safety.

        Args:
            data: Data to write.

        Raises:
            ConfigurationError: If write operation fails.
        """
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise ConfigurationError(f"Failed to write {self.db_path}: {str(e)}")

    def register_tutor(
        self, telegram_id: str, name: str, sheets_id: str
    ) -> TutorConfig:
        """Register a new tutor.

        Args:
            telegram_id: Tutor's Telegram ID.
            name: Tutor's name.
            sheets_id: Google Sheets ID for tutor's spreadsheet.

        Returns:
            TutorConfig object.

        Raises:
            TutorAlreadyExistsError: If tutor with same telegram_id already exists.
            ConfigurationError: If database operation fails.
        """
        with self._lock:
            db_data = self._read_db()

            for tutor in db_data.get("tutors", []):
                if tutor.get("telegram_id") == telegram_id:
                    raise TutorAlreadyExistsError(
                        f"Tutor with telegram_id {telegram_id} already registered"
                    )

            now = datetime.now().isoformat()
            tutor_config = TutorConfig(
                telegram_id=telegram_id,
                name=name,
                sheets_id=sheets_id,
                created_at=now,
                updated_at=now,
            )

            db_data["tutors"].append(tutor_config.to_dict())
            self._write_db(db_data)

            return tutor_config

    def get_tutor(self, telegram_id: str) -> TutorConfig:
        """Get tutor by telegram_id.

        Args:
            telegram_id: Tutor's Telegram ID.

        Returns:
            TutorConfig object.

        Raises:
            TutorNotFoundError: If tutor is not found.
        """
        with self._lock:
            db_data = self._read_db()

            for tutor_data in db_data.get("tutors", []):
                if tutor_data.get("telegram_id") == telegram_id:
                    return TutorConfig.from_dict(tutor_data)

            raise TutorNotFoundError(
                f"Tutor with telegram_id {telegram_id} not found"
            )

    def update_tutor(self, telegram_id: str, **kwargs) -> TutorConfig:
        """Update tutor configuration.

        Args:
            telegram_id: Tutor's Telegram ID.
            **kwargs: Fields to update (name, sheets_id).

        Returns:
            Updated TutorConfig object.

        Raises:
            TutorNotFoundError: If tutor is not found.
            ConfigurationError: If database operation fails.
        """
        with self._lock:
            db_data = self._read_db()

            found = False
            for tutor in db_data.get("tutors", []):
                if tutor.get("telegram_id") == telegram_id:
                    for key, value in kwargs.items():
                        if key in ("name", "sheets_id"):
                            tutor[key] = value
                    tutor["updated_at"] = datetime.now().isoformat()
                    found = True
                    break

            if not found:
                raise TutorNotFoundError(
                    f"Tutor with telegram_id {telegram_id} not found"
                )

            self._write_db(db_data)
            return TutorConfig.from_dict(tutor)

    def delete_tutor(self, telegram_id: str) -> None:
        """Delete a tutor registration.

        Args:
            telegram_id: Tutor's Telegram ID.

        Raises:
            TutorNotFoundError: If tutor is not found.
            ConfigurationError: If database operation fails.
        """
        with self._lock:
            db_data = self._read_db()

            initial_length = len(db_data.get("tutors", []))
            db_data["tutors"] = [
                t
                for t in db_data.get("tutors", [])
                if t.get("telegram_id") != telegram_id
            ]

            if len(db_data["tutors"]) == initial_length:
                raise TutorNotFoundError(
                    f"Tutor with telegram_id {telegram_id} not found"
                )

            self._write_db(db_data)

    def list_tutors(self) -> List[TutorConfig]:
        """List all registered tutors.

        Returns:
            List of TutorConfig objects.
        """
        with self._lock:
            db_data = self._read_db()
            return [
                TutorConfig.from_dict(tutor) for tutor in db_data.get("tutors", [])
            ]

    def tutor_exists(self, telegram_id: str) -> bool:
        """Check if tutor exists.

        Args:
            telegram_id: Tutor's Telegram ID.

        Returns:
            True if tutor exists, False otherwise.
        """
        try:
            self.get_tutor(telegram_id)
            return True
        except TutorNotFoundError:
            return False
