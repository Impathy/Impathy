"""Custom exceptions for database and sheets operations."""


class SheetsBackendError(Exception):
    """Base exception for all sheets backend errors."""
    pass


class AuthenticationError(SheetsBackendError):
    """Raised when authentication with Google Sheets fails."""
    pass


class SheetNotFoundError(SheetsBackendError):
    """Raised when a spreadsheet cannot be found or accessed."""
    pass


class WorksheetNotFoundError(SheetsBackendError):
    """Raised when a required worksheet is not found in the spreadsheet."""
    pass


class MalformedDataError(SheetsBackendError):
    """Raised when data in sheets is malformed or invalid."""
    pass


class TutorNotFoundError(SheetsBackendError):
    """Raised when a tutor entry is not found in tutors_db."""
    pass


class TutorAlreadyExistsError(SheetsBackendError):
    """Raised when trying to register a tutor that already exists."""
    pass


class ConfigurationError(SheetsBackendError):
    """Raised when configuration files are missing or invalid."""
    pass
