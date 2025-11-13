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
