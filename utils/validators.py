"""Input validation utilities for the bot."""

import re
from typing import Optional


def extract_sheet_id(input_string: str) -> Optional[str]:
    """Extract Google Sheets ID from a URL or return the input if it looks like an ID.

    Args:
        input_string: Either a Google Sheets URL or a spreadsheet ID.

    Returns:
        The extracted sheet ID, or None if the input is invalid.

    Examples:
        >>> extract_sheet_id('https://docs.google.com/spreadsheets/d/1ABC2DEF/edit')
        '1ABC2DEF'
        >>> extract_sheet_id('1ABC2DEF')
        '1ABC2DEF'
        >>> extract_sheet_id('invalid')
        None
    """
    input_string = input_string.strip()

    # Try to extract from URL
    url_pattern = r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(url_pattern, input_string)
    if match:
        return match.group(1)

    # Check if it's a valid sheet ID format (alphanumeric with hyphens and underscores)
    if re.match(r'^[a-zA-Z0-9-_]+$', input_string) and len(input_string) > 10:
        return input_string

    return None


def validate_name(name: str) -> bool:
    """Validate a tutor name.

    Args:
        name: The name to validate.

    Returns:
        True if the name is valid, False otherwise.
    """
    name = name.strip()
    # Name should be at least 2 characters and at most 100 characters
    # Allow letters, digits, spaces, and common punctuation
    if not name or len(name) < 2 or len(name) > 100:
        return False
    # Allow letters, digits, spaces, hyphens, and apostrophes
    return bool(re.match(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-']+$", name))


def sanitize_name(name: str) -> str:
    """Sanitize a tutor name by stripping whitespace.

    Args:
        name: The name to sanitize.

    Returns:
        The sanitized name.
    """
    return ' '.join(name.strip().split())
