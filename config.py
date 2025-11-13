import os
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class BotCommands(Enum):
    """Telegram bot command names."""
    HEALTH = "health"
    START = "start"
    HELP = "help"
    REGISTER = "register"
    PROFILE = "profile"
    ADD_STUDENT = "add_student"
    LIST_STUDENTS = "list_students"
    DELETE_STUDENT = "delete_student"


class SheetNames(Enum):
    """Google Sheets sheet names."""
    TUTORS = "Tutors"
    SCHEDULE = "Schedule"
    ATTENDANCE = "Attendance"
    STUDENTS = "Ученики"


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")
TUTORS_CONFIG_PATH = os.getenv("TUTORS_CONFIG_PATH", "tutors_config.json")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def validate_config():
    """Validate that required configuration is present."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    credentials_file = BASE_DIR / CREDENTIALS_PATH
    tutors_config_file = BASE_DIR / TUTORS_CONFIG_PATH
    
    if not credentials_file.exists():
        raise FileNotFoundError(
            f"Credentials file not found at {credentials_file}. "
            "Please ensure credentials.json is in the project root."
        )
    
    if not tutors_config_file.exists():
        raise FileNotFoundError(
            f"Tutors config file not found at {tutors_config_file}. "
            "Please ensure tutors_config.json is in the project root."
        )
