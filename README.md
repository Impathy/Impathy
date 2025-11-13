# Telegram Bot Project

A Telegram bot for managing tutors, schedules, and attendance with Google Sheets integration.

## Project Structure

```
.
├── handlers/           # Telegram bot command handlers
├── database/          # Database operations and Google Sheets integration
├── scheduler/         # Scheduled tasks and background jobs
├── utils/            # Utility functions and helper modules
├── config.py         # Configuration and environment variables
├── main.py           # Bot startup and main entry point
├── requirements.txt  # Python dependencies
├── .env              # Environment variables (not in git)
├── .env.example      # Example environment variables
├── credentials.json  # Google Service Account credentials (not in git)
└── tutors_config.json # Tutors configuration (not in git)
```

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (obtain from [@BotFather](https://t.me/botfather))
- Google Service Account credentials with Google Sheets API access

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and update it with your values:

```bash
cp .env.example .env
```

Edit `.env` and set the following:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
- `CREDENTIALS_PATH`: Path to your Google Service Account credentials file (default: `credentials.json`)
- `TUTORS_CONFIG_PATH`: Path to your tutors configuration file (default: `tutors_config.json`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### 5. Set up Google Service Account

To integrate with Google Sheets, you need to set up a Google Service Account:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API for your project:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create a Service Account:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the service account details and create
5. Create and download a key:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Save the downloaded file as `credentials.json` in the project root
6. Share your Google Sheets with the service account email:
   - Open your Google Sheet
   - Click "Share"
   - Add the service account email (found in `credentials.json` as `client_email`)
   - Give it "Editor" permissions

### 6. Create tutors configuration

Create a `tutors_config.json` file in the project root with your tutors configuration:

```json
{
  "tutors": [
    {
      "id": "1",
      "name": "John Doe",
      "telegram_id": 123456789,
      "subjects": ["Math", "Physics"]
    }
  ]
}
```

## Running the Bot

### Local Development

To run the bot locally:

```bash
python main.py
```

The bot will start polling for messages. You should see log output indicating the bot has started successfully.

### Testing the Bot

Once the bot is running, you can test it in Telegram:

1. Find your bot by its username on Telegram
2. Start a chat with the bot
3. Try the `/health` command to verify the bot is running

Expected response:
```
✅ Bot is running and healthy!
Credentials path: credentials.json
Tutors config path: tutors_config.json
```

## Available Commands

- `/health` - Check bot status and configuration

More commands will be added as the project develops.

## Development

### Project Components

- **handlers/**: Contains Telegram command handlers for bot interactions
- **database/**: Manages Google Sheets integration and data operations
- **scheduler/**: Implements scheduled tasks (e.g., attendance reminders)
- **utils/**: Common utility functions and helpers
- **config.py**: Centralizes configuration, environment variables, and constants
- **main.py**: Bot initialization and startup logic

### Adding New Dependencies

When adding new Python packages:

1. Install the package: `pip install package-name`
2. Update requirements.txt: `pip freeze > requirements.txt`

### Code Quality

To check if the code compiles without errors:

```bash
python -m compileall .
```

## Troubleshooting

### Bot token invalid

- Verify your `TELEGRAM_BOT_TOKEN` in `.env` is correct
- Make sure you copied the token exactly from BotFather

### Credentials file not found

- Ensure `credentials.json` exists in the project root
- Check the path specified in `CREDENTIALS_PATH` in `.env`

### Import errors

- Make sure you're in the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## License

[Specify your license here]

## Contributing

[Add contribution guidelines here]
# Tutor Sheets Backend

A Python backend for managing tutor data through Google Sheets with thread-safe database operations.

## Features

- **Google Sheets Integration**: Read and write student, lesson, and payment data to Google Sheets
- **Tutor Configuration Management**: Register and manage tutor accounts with thread-safe operations
- **Data Models**: Type-safe data classes for Students, Lessons, Payments, and Tutor configurations
- **Automatic Worksheet Creation**: Automatically creates missing worksheets with proper headers
- **Custom Exceptions**: Clear error handling with specific exception types
- **Thread Safety**: Concurrent access to tutor database is thread-safe

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd project
```

2. Install dependencies:
```bash
pip install gspread oauth2client
```

## Setup

### Creating a Google Sheet Template

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet
2. The spreadsheet will be auto-populated with the following sheets when first accessed:
   - **Ученики** (Students): Name, Telegram ID, Email, Phone, Notes
   - **Уроки** (Lessons): Student Name, Date, Time, Duration, Topic, Notes
   - **Платежи** (Payments): Student Name, Amount, Date, Payment Method, Notes
   - **История** (History): Date, Event, Details
   - **Настройки** (Settings): Key, Value

3. Note the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
   ```

### Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to "Service Accounts" in the IAM & Admin section
   - Click "Create Service Account"
   - Fill in the service account details
   - Skip optional steps
5. Create a key for the service account:
   - Go to the service account details
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose JSON format
   - The key file will download automatically
6. Save the key file as `credentials.json` in the project root

### Sharing the Spreadsheet

1. Share the Google Sheet with the service account email:
   - Open the spreadsheet
   - Click "Share"
   - Paste the service account email (found in `credentials.json` under `client_email`)
   - Give the service account Editor permissions
   - Make sure to share with "Anyone with the link" or specifically with the service account

## Usage

### Basic Setup

```python
from database.sheets_manager import SheetsManager
from database.tutors_db import TutorsDB
from utils.models import Student, Lesson, Payment

# Initialize managers
sheets_manager = SheetsManager('credentials.json')
tutors_db = TutorsDB('tutors_config.json')
```

### Register a Tutor

```python
tutor_config = tutors_db.register_tutor(
    telegram_id="123456789",
    name="Иван Петров",
    sheets_id="1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4"
)
```

### Working with Students

```python
# Get all students
students = sheets_manager.get_all_students(tutor_config.sheets_id)

# Add a new student
student = Student(
    name="Мария",
    telegram_id="987654321",
    email="maria@example.com",
    phone="+79991234567"
)
sheets_manager.add_student(tutor_config.sheets_id, student)

# Update a student (requires sheet_row to be set)
student.sheet_row = 2  # Row 2 in the sheet
sheets_manager.update_student(tutor_config.sheets_id, student)
```

### Working with Lessons

```python
# Get all lessons
lessons = sheets_manager.get_all_lessons(tutor_config.sheets_id)

# Add a new lesson
lesson = Lesson(
    student_name="Мария",
    date="2024-01-15",
    time="15:30",
    duration="60",
    topic="Математика",
    notes="Изучаем тригонометрию"
)
sheets_manager.add_lesson(tutor_config.sheets_id, lesson)
```

### Working with Payments

```python
# Get all payments
payments = sheets_manager.get_all_payments(tutor_config.sheets_id)

# Add a payment
payment = Payment(
    student_name="Мария",
    amount="3000",
    date="2024-01-15",
    method="Перевод",
    notes="Оплата за месяц"
)
sheets_manager.add_payment(tutor_config.sheets_id, payment)
```

### Logging Events

```python
sheets_manager.log_event(
    tutor_config.sheets_id,
    event="Student registered",
    detail="New student: Maria"
)
```

### Managing Settings

```python
# Get a setting
rate = sheets_manager.get_setting(tutor_config.sheets_id, "hourly_rate")

# Set a setting
sheets_manager.set_setting(tutor_config.sheets_id, "hourly_rate", "1500")
```

### Tutor Database Operations

```python
# Get a tutor
tutor = tutors_db.get_tutor("123456789")

# Update a tutor
tutors_db.update_tutor("123456789", name="Иван Петров Updated")

# List all tutors
all_tutors = tutors_db.list_tutors()

# Check if tutor exists
exists = tutors_db.tutor_exists("123456789")

# Delete a tutor
tutors_db.delete_tutor("123456789")
```

## Project Structure

```
project/
├── database/
│   ├── __init__.py
│   ├── exceptions.py          # Custom exception classes
│   ├── sheets_manager.py      # Google Sheets operations
│   └── tutors_db.py          # Tutor database management
├── utils/
│   ├── __init__.py
│   └── models.py             # Data models and dataclasses
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # Model tests
│   ├── test_sheets_manager.py # Sheets manager tests
│   └── test_tutors_db.py     # Database tests
├── credentials.json          # Service account credentials (create during setup)
├── tutors_config.json        # Tutor registrations (auto-created)
└── README.md
```

## Data Models

### Student
```python
@dataclass
class Student:
    name: str
    telegram_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    sheet_row: Optional[int] = None
```

### Lesson
```python
@dataclass
class Lesson:
    student_name: str
    date: str
    time: Optional[str] = None
    duration: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    sheet_row: Optional[int] = None
```

### Payment
```python
@dataclass
class Payment:
    student_name: str
    amount: str
    date: str
    method: Optional[str] = None
    notes: Optional[str] = None
    sheet_row: Optional[int] = None
```

### TutorConfig
```python
@dataclass
class TutorConfig:
    telegram_id: str
    name: str
    sheets_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

## Error Handling

The system provides specific exception types for different error scenarios:

- `AuthenticationError`: Failed to authenticate with Google Sheets
- `SheetNotFoundError`: Spreadsheet cannot be found or accessed
- `WorksheetNotFoundError`: Required worksheet is missing
- `MalformedDataError`: Data in sheets is invalid
- `TutorNotFoundError`: Tutor entry not found in database
- `TutorAlreadyExistsError`: Attempting to register duplicate tutor
- `ConfigurationError`: Configuration files are missing or invalid

Example:
```python
from database.exceptions import TutorNotFoundError

try:
    tutor = tutors_db.get_tutor("nonexistent")
except TutorNotFoundError as e:
    print(f"Error: {e}")
```

## Thread Safety

The `TutorsDB` class is thread-safe and uses locks to ensure that concurrent operations don't corrupt data:

```python
from threading import Thread
from database.tutors_db import TutorsDB

db = TutorsDB('tutors_config.json')

def register_tutors():
    for i in range(10):
        db.register_tutor(f"tutor-{i}", f"Tutor {i}", f"sheet-{i}")

threads = [Thread(target=register_tutors) for _ in range(3)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=database --cov=utils tests/
```

## Example: Complete Workflow

```python
from database.sheets_manager import SheetsManager
from database.tutors_db import TutorsDB
from utils.models import Student, Lesson, Payment

# 1. Register a tutor
tutors_db = TutorsDB()
tutor = tutors_db.register_tutor(
    telegram_id="123456789",
    name="Иван Петров",
    sheets_id="1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4"
)

# 2. Initialize sheets manager
sheets_manager = SheetsManager()

# 3. Ensure all worksheets exist
spreadsheet = sheets_manager.open_spreadsheet(tutor.sheets_id)
worksheets = sheets_manager.ensure_all_worksheets(spreadsheet)

# 4. Add a student
student = Student(
    name="Мария",
    telegram_id="987654321",
    email="maria@example.com"
)
sheets_manager.add_student(tutor.sheets_id, student)

# 5. Add a lesson
lesson = Lesson(
    student_name="Мария",
    date="2024-01-15",
    time="15:30",
    duration="60",
    topic="Математика"
)
sheets_manager.add_lesson(tutor.sheets_id, lesson)

# 6. Log the event
sheets_manager.log_event(tutor.sheets_id, "Lesson recorded", "Maria - Math")

# 7. Verify students were added
students = sheets_manager.get_all_students(tutor.sheets_id)
print(f"Total students: {len(students)}")
```

## Troubleshooting

### "Credentials file not found"
- Make sure `credentials.json` is in the project root
- Check that the path to credentials.json is correct

### "Spreadsheet not found"
- Verify the sheet ID is correct
- Make sure the service account has access to the spreadsheet
- Check that the spreadsheet was shared with the service account email

### "Authentication failed"
- Ensure the `credentials.json` file contains valid Google service account credentials
- Check that the service account email is correctly added to the spreadsheet

### "Permission denied"
- Make sure the service account email has Editor access to the spreadsheet
- Go to the spreadsheet and verify the sharing settings

## License

This project is provided as-is for internal use.

## Support

For issues or questions, please contact the development team.
