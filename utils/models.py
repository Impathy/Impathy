"""Data models and dataclasses for Sheets backend."""

from dataclasses import dataclass, asdict, field
from typing import Optional, Any, Dict, List
from datetime import datetime


@dataclass
class Student:
    """Model for a student record."""
    name: str
    telegram_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    sheet_row: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_row(self) -> List[str]:
        """Convert to row format for sheets."""
        return [
            self.name,
            self.telegram_id or "",
            self.email or "",
            self.phone or "",
            self.notes or "",
        ]

    @classmethod
    def from_row(cls, row: List[str], sheet_row: int = 0) -> "Student":
        """Create from row data."""
        return cls(
            name=row[0] if len(row) > 0 else "",
            telegram_id=row[1] if len(row) > 1 and row[1] else None,
            email=row[2] if len(row) > 2 and row[2] else None,
            phone=row[3] if len(row) > 3 and row[3] else None,
            notes=row[4] if len(row) > 4 and row[4] else None,
            sheet_row=sheet_row,
        )


@dataclass
class Lesson:
    """Model for a lesson record."""
    student_name: str
    date: str
    time: Optional[str] = None
    duration: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    sheet_row: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_row(self) -> List[str]:
        """Convert to row format for sheets."""
        return [
            self.student_name,
            self.date,
            self.time or "",
            self.duration or "",
            self.topic or "",
            self.notes or "",
        ]

    @classmethod
    def from_row(cls, row: List[str], sheet_row: int = 0) -> "Lesson":
        """Create from row data."""
        return cls(
            student_name=row[0] if len(row) > 0 else "",
            date=row[1] if len(row) > 1 else "",
            time=row[2] if len(row) > 2 and row[2] else None,
            duration=row[3] if len(row) > 3 and row[3] else None,
            topic=row[4] if len(row) > 4 and row[4] else None,
            notes=row[5] if len(row) > 5 and row[5] else None,
            sheet_row=sheet_row,
        )


@dataclass
class Payment:
    """Model for a payment record."""
    student_name: str
    amount: str
    date: str
    method: Optional[str] = None
    notes: Optional[str] = None
    sheet_row: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_row(self) -> List[str]:
        """Convert to row format for sheets."""
        return [
            self.student_name,
            self.amount,
            self.date,
            self.method or "",
            self.notes or "",
        ]

    @classmethod
    def from_row(cls, row: List[str], sheet_row: int = 0) -> "Payment":
        """Create from row data."""
        return cls(
            student_name=row[0] if len(row) > 0 else "",
            amount=row[1] if len(row) > 1 else "",
            date=row[2] if len(row) > 2 else "",
            method=row[3] if len(row) > 3 and row[3] else None,
            notes=row[4] if len(row) > 4 and row[4] else None,
            sheet_row=sheet_row,
        )


@dataclass
class TutorConfig:
    """Model for tutor configuration."""
    telegram_id: str
    name: str
    sheets_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TutorConfig":
        """Create from dictionary."""
        return cls(
            telegram_id=data["telegram_id"],
            name=data["name"],
            sheets_id=data["sheets_id"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
