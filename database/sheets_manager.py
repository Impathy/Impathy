"""Google Sheets manager for tutor applications."""

import os
import json
from typing import List, Optional, Dict, Any

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from .exceptions import (
    AuthenticationError,
    SheetNotFoundError,
    WorksheetNotFoundError,
    MalformedDataError,
)
from utils.models import Student, Lesson, Payment


SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

WORKSHEET_HEADERS = {
    "Ученики": ["Имя", "Telegram ID", "Email", "Телефон", "Заметки"],
    "Уроки": ["Студент", "Дата", "Время", "Продолжительность", "Тема", "Заметки"],
    "Платежи": ["Студент", "Сумма", "Дата", "Метод оплаты", "Заметки"],
    "История": ["Дата", "Событие", "Деталь"],
    "Настройки": ["Ключ", "Значение"],
}


class SheetsManager:
    """Manager for Google Sheets operations."""

    def __init__(self, credentials_path: str = "credentials.json"):
        """Initialize sheets manager with credentials.

        Args:
            credentials_path: Path to Google service account credentials JSON file.

        Raises:
            AuthenticationError: If credentials file is not found or invalid.
        """
        if not os.path.exists(credentials_path):
            raise AuthenticationError(
                f"Credentials file not found at {credentials_path}"
            )

        try:
            self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_path, scopes=SCOPES
            )
            self.client = gspread.authorize(self.credentials)
        except (IOError, json.JSONDecodeError, ValueError) as e:
            raise AuthenticationError(f"Failed to authenticate: {str(e)}")

    def open_spreadsheet(self, sheet_id: str) -> gspread.Spreadsheet:
        """Open a spreadsheet by ID.

        Args:
            sheet_id: Google Sheets ID.

        Returns:
            gspread Spreadsheet object.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
        """
        try:
            return self.client.open_by_key(sheet_id)
        except gspread.exceptions.SpreadsheetNotFound:
            raise SheetNotFoundError(f"Spreadsheet with ID {sheet_id} not found")
        except Exception as e:
            raise SheetNotFoundError(f"Failed to open spreadsheet: {str(e)}")

    def ensure_worksheet_exists(
        self, spreadsheet: gspread.Spreadsheet, worksheet_name: str
    ) -> gspread.Worksheet:
        """Ensure a worksheet exists, creating it if necessary.

        Args:
            spreadsheet: gspread Spreadsheet object.
            worksheet_name: Name of the worksheet.

        Returns:
            gspread Worksheet object.

        Raises:
            WorksheetNotFoundError: If worksheet cannot be created.
        """
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            try:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name, rows=1000, cols=26
                )
                headers = WORKSHEET_HEADERS.get(worksheet_name, [])
                if headers:
                    worksheet.append_row(headers)
            except Exception as e:
                raise WorksheetNotFoundError(
                    f"Failed to create worksheet {worksheet_name}: {str(e)}"
                )

        return worksheet

    def ensure_all_worksheets(
        self, spreadsheet: gspread.Spreadsheet
    ) -> Dict[str, gspread.Worksheet]:
        """Ensure all required worksheets exist.

        Args:
            spreadsheet: gspread Spreadsheet object.

        Returns:
            Dictionary mapping worksheet names to worksheet objects.
        """
        worksheets = {}
        for worksheet_name in WORKSHEET_HEADERS.keys():
            worksheets[worksheet_name] = self.ensure_worksheet_exists(
                spreadsheet, worksheet_name
            )
        return worksheets

    def get_all_students(self, sheet_id: str) -> List[Student]:
        """Get all students from the spreadsheet.

        Args:
            sheet_id: Google Sheets ID.

        Returns:
            List of Student objects.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Ученики worksheet is not found.
            MalformedDataError: If student data is invalid.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Ученики")

        students = []
        rows = worksheet.get_all_values()

        for idx, row in enumerate(rows[1:], start=2):
            if not row or not row[0]:
                continue
            try:
                student = Student.from_row(row, sheet_row=idx)
                students.append(student)
            except (IndexError, ValueError) as e:
                raise MalformedDataError(
                    f"Invalid student data at row {idx}: {str(e)}"
                )

        return students

    def get_all_lessons(self, sheet_id: str) -> List[Lesson]:
        """Get all lessons from the spreadsheet.

        Args:
            sheet_id: Google Sheets ID.

        Returns:
            List of Lesson objects.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Уроки worksheet is not found.
            MalformedDataError: If lesson data is invalid.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Уроки")

        lessons = []
        rows = worksheet.get_all_values()

        for idx, row in enumerate(rows[1:], start=2):
            if not row or not row[0]:
                continue
            try:
                lesson = Lesson.from_row(row, sheet_row=idx)
                lessons.append(lesson)
            except (IndexError, ValueError) as e:
                raise MalformedDataError(f"Invalid lesson data at row {idx}: {str(e)}")

        return lessons

    def get_all_payments(self, sheet_id: str) -> List[Payment]:
        """Get all payments from the spreadsheet.

        Args:
            sheet_id: Google Sheets ID.

        Returns:
            List of Payment objects.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Платежи worksheet is not found.
            MalformedDataError: If payment data is invalid.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Платежи")

        payments = []
        rows = worksheet.get_all_values()

        for idx, row in enumerate(rows[1:], start=2):
            if not row or not row[0]:
                continue
            try:
                payment = Payment.from_row(row, sheet_row=idx)
                payments.append(payment)
            except (IndexError, ValueError) as e:
                raise MalformedDataError(
                    f"Invalid payment data at row {idx}: {str(e)}"
                )

        return payments

    def add_student(self, sheet_id: str, student: Student) -> None:
        """Add a student to the spreadsheet.

        Args:
            sheet_id: Google Sheets ID.
            student: Student object to add.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Ученики worksheet is not found.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Ученики")
        worksheet.append_row(student.to_row())

    def add_lesson(self, sheet_id: str, lesson: Lesson) -> None:
        """Add a lesson to the spreadsheet.

        Args:
            sheet_id: Google Sheets ID.
            lesson: Lesson object to add.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Уроки worksheet is not found.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Уроки")
        worksheet.append_row(lesson.to_row())

    def add_payment(self, sheet_id: str, payment: Payment) -> None:
        """Add a payment to the spreadsheet.

        Args:
            sheet_id: Google Sheets ID.
            payment: Payment object to add.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Платежи worksheet is not found.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Платежи")
        worksheet.append_row(payment.to_row())

    def log_event(self, sheet_id: str, event: str, detail: str = "") -> None:
        """Log an event to the История worksheet.

        Args:
            sheet_id: Google Sheets ID.
            event: Event description.
            detail: Optional event detail.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If История worksheet is not found.
        """
        from datetime import datetime

        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "История")
        worksheet.append_row([datetime.now().isoformat(), event, detail])

    def get_setting(self, sheet_id: str, key: str) -> Optional[str]:
        """Get a setting value from Настройки worksheet.

        Args:
            sheet_id: Google Sheets ID.
            key: Setting key.

        Returns:
            Setting value or None if not found.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Настройки worksheet is not found.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Настройки")
        rows = worksheet.get_all_values()

        for row in rows[1:]:
            if row and len(row) > 0 and row[0] == key:
                return row[1] if len(row) > 1 else None

        return None

    def set_setting(self, sheet_id: str, key: str, value: str) -> None:
        """Set or update a setting in Настройки worksheet.

        Args:
            sheet_id: Google Sheets ID.
            key: Setting key.
            value: Setting value.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Настройки worksheet is not found.
        """
        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Настройки")
        rows = worksheet.get_all_values()

        for idx, row in enumerate(rows[1:], start=2):
            if row and len(row) > 0 and row[0] == key:
                worksheet.update_cell(idx, 2, value)
                return

        worksheet.append_row([key, value])

    def update_student(self, sheet_id: str, student: Student) -> None:
        """Update a student record.

        Args:
            sheet_id: Google Sheets ID.
            student: Student object with sheet_row set.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Ученики worksheet is not found.
            ValueError: If sheet_row is not set.
        """
        if student.sheet_row is None:
            raise ValueError("sheet_row must be set for update operations")

        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Ученики")
        row_data = student.to_row()

        for col_idx, value in enumerate(row_data, start=1):
            worksheet.update_cell(student.sheet_row, col_idx, value)

    def update_lesson(self, sheet_id: str, lesson: Lesson) -> None:
        """Update a lesson record.

        Args:
            sheet_id: Google Sheets ID.
            lesson: Lesson object with sheet_row set.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Уроки worksheet is not found.
            ValueError: If sheet_row is not set.
        """
        if lesson.sheet_row is None:
            raise ValueError("sheet_row must be set for update operations")

        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Уроки")
        row_data = lesson.to_row()

        for col_idx, value in enumerate(row_data, start=1):
            worksheet.update_cell(lesson.sheet_row, col_idx, value)

    def update_payment(self, sheet_id: str, payment: Payment) -> None:
        """Update a payment record.

        Args:
            sheet_id: Google Sheets ID.
            payment: Payment object with sheet_row set.

        Raises:
            SheetNotFoundError: If spreadsheet cannot be opened.
            WorksheetNotFoundError: If Платежи worksheet is not found.
            ValueError: If sheet_row is not set.
        """
        if payment.sheet_row is None:
            raise ValueError("sheet_row must be set for update operations")

        spreadsheet = self.open_spreadsheet(sheet_id)
        worksheet = self.ensure_worksheet_exists(spreadsheet, "Платежи")
        row_data = payment.to_row()

        for col_idx, value in enumerate(row_data, start=1):
            worksheet.update_cell(payment.sheet_row, col_idx, value)
