# Auth Handlers - Manual Testing Guide

This document outlines the manual testing procedures for the authentication and registration handlers.

## Overview

The auth handlers implement the following functionality:
- **`/start`** - Differentiates between registered and new tutors
- **`/register`** - Handles user registration flow (conversation handler)
- **`/profile`** - Displays tutor profile information
- **`/help`** - Shows available commands

## Prerequisites

1. Running Telegram bot with credentials configured
2. Access to Google Sheets API credentials
3. A test Google Sheet created and shared with the service account

## Test Scenarios

### Scenario 1: New User Registration Flow

**Objective:** Verify that a new user can complete the registration process successfully.

**Steps:**
1. Open Telegram and find your test bot
2. Send `/start` command
   - **Expected:** Bot displays welcome message for new users with `/register` and `/help` buttons
3. Send `/register` command
   - **Expected:** Bot asks for the tutor's name
4. Enter a valid name (e.g., "John Doe")
   - **Expected:** Bot confirms the name and asks for Google Sheet URL/ID
5. Enter a valid Google Sheet URL (format: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`)
   - **Expected:** Bot validates the sheet, creates required worksheets, and confirms successful registration
   - Worksheets created: "Ученики", "Уроки", "Платежи", "История", "Настройки"
6. Send `/profile` command
   - **Expected:** Bot displays the registered tutor's profile information

**Pass Criteria:**
- All prompts appear as expected
- Registration completes without errors
- Profile shows correct name and sheet ID

---

### Scenario 2: Invalid Sheet URL Handling

**Objective:** Verify that invalid sheet URLs are rejected gracefully.

**Steps:**
1. Send `/register` command (if starting new session)
   - **Expected:** Bot asks for the tutor's name
2. Enter a valid name
   - **Expected:** Bot asks for sheet URL/ID
3. Enter an invalid URL (e.g., `https://example.com` or random text)
   - **Expected:** Bot shows error about invalid format
   - Bot asks to re-enter the sheet URL/ID
4. Enter a valid sheet ID
   - **Expected:** Registration proceeds successfully

**Pass Criteria:**
- Invalid URLs are rejected
- User can retry without restarting conversation
- Valid sheet ID is accepted after retry

---

### Scenario 3: Sheet Access Error Handling

**Objective:** Verify that inaccessible sheets are rejected with helpful error messages.

**Steps:**
1. Send `/register` command
   - **Expected:** Bot asks for tutor's name
2. Enter a valid name
   - **Expected:** Bot asks for sheet URL/ID
3. Enter a valid-format sheet ID that doesn't exist or isn't shared
   - **Expected:** Bot shows error about unable to access sheet
   - Error message includes: "Проверьте, что: 1. ID таблицы правильный 2. Таблица открыта 3. Сервис-аккаунт имеет доступ"
4. Enter a valid, accessible sheet ID
   - **Expected:** Registration proceeds successfully

**Pass Criteria:**
- Non-existent sheets are rejected
- Helpful error messages are shown
- User can retry with another sheet

---

### Scenario 4: Duplicate Registration Prevention

**Objective:** Verify that already-registered users cannot register again.

**Steps:**
1. Complete registration (Scenario 1) if not already done
2. Send `/register` command
   - **Expected:** Bot shows message indicating user is already registered
   - Bot suggests using `/profile` to view current information
   - Conversation ends without prompting for new information

**Pass Criteria:**
- Duplicate registration is prevented
- User is informed they're already registered
- Helpful guidance is provided

---

### Scenario 5: Registered User Start Command

**Objective:** Verify that registered users see a different menu.

**Steps:**
1. Ensure you've completed registration (Scenario 1)
2. Send `/start` command
   - **Expected:** Bot shows personalized welcome message with tutor's name
   - Menu shows `/profile` and `/help` options (not `/register`)

**Pass Criteria:**
- Registered users see personalized greeting
- Registration option is not shown for registered users
- Profile option is available

---

### Scenario 6: Profile Display

**Objective:** Verify that profile information is displayed correctly.

**Steps:**
1. Complete registration if not already done
2. Send `/profile` command
   - **Expected:** Bot displays:
     - Tutor's registered name
     - Link to Google Sheet
     - Registration date (formatted as DD.MM.YYYY HH:MM)
     - Last update date
     - All information in a formatted box

**Pass Criteria:**
- All profile fields are displayed
- Dates are properly formatted
- Sheet link is clickable and correct

---

### Scenario 7: Unregistered User Profile Request

**Objective:** Verify that unregistered users cannot access profile.

**Steps:**
1. In a new chat or after clearing data
2. Send `/profile` command without registering
   - **Expected:** Bot shows error message: "Вы не зарегистрированы"
   - Suggests using `/register` to register

**Pass Criteria:**
- Profile command is restricted to registered users
- Clear error message is shown
- Helpful guidance is provided

---

### Scenario 8: Help Command

**Objective:** Verify that help information is displayed correctly.

**Steps:**
1. Send `/help` command
   - **Expected:** Bot displays help text with all available commands:
     - /start
     - /register
     - /profile
     - /help

**Pass Criteria:**
- All commands are listed
- Help text is clear and informative

---

### Scenario 9: Registration Cancellation

**Objective:** Verify that users can cancel registration mid-flow.

**Steps:**
1. Send `/register` command
   - **Expected:** Bot asks for name
2. Send `/cancel` command
   - **Expected:** Bot confirms cancellation and ends conversation
3. Send `/register` again
   - **Expected:** Registration starts fresh from the beginning

**Pass Criteria:**
- Cancel command ends the conversation
- New registration can be started after cancellation
- No partial data is retained

---

### Scenario 10: Invalid Name Input

**Objective:** Verify that invalid names are rejected.

**Steps:**
1. Send `/register` command
2. Enter an invalid name (e.g., just one character "A" or special characters "###")
   - **Expected:** Bot shows error about invalid input
   - Bot asks for name again
3. Enter a valid name
   - **Expected:** Conversation proceeds to sheet URL/ID request

**Pass Criteria:**
- Invalid names are rejected
- Error message is shown
- User can retry without restarting

---

## Automated Test Verification

### Unit Tests

Unit tests are available in `tests/test_tutors_db.py` and validate:
- Tutor registration
- Tutor retrieval
- Duplicate registration prevention
- Tutor updates

Run with:
```bash
pytest tests/test_tutors_db.py -v
```

### Integration Tests

Integration tests in `tests/test_integration.py` validate:
- End-to-end registration flow
- Sheet validation
- Database consistency

Run with:
```bash
pytest tests/test_integration.py -v
```

### Validators Unit Tests

Test input validation with:
```bash
pytest tests/ -v -k "validator"
```

---

## Test Data

### Sample Valid Sheet URL
```
https://docs.google.com/spreadsheets/d/1ABC2DEF3GHI4JKL5MNO6PQR7STU8VWX9YZ/edit
```

### Sample Valid Sheet ID
```
1ABC2DEF3GHI4JKL5MNO6PQR7STU8VWX9YZ
```

### Sample Invalid Inputs
- `https://example.com`
- `just-a-random-text`
- `123`
- `!!!`

---

## Troubleshooting

### Bot doesn't respond to /start
- Check that the bot is running: `python main.py`
- Verify TELEGRAM_BOT_TOKEN is set in `.env`
- Check bot logs for errors

### "Sheet not found" error during registration
- Verify sheet ID is correct
- Confirm the sheet is shared with the service account email (in `credentials.json`)
- Check that the sheet is not in trash
- Verify Google Sheets API is enabled

### "Registration failed" error
- Check `tutors_config.json` exists and is writable
- Verify file permissions: `chmod 644 tutors_config.json`
- Check disk space available

### Profile shows incorrect dates
- Verify system timezone is correct
- Check `updated_at` field in `tutors_config.json` is valid ISO format

---

## Expected Database State After Successful Registration

After completing registration, the `tutors_config.json` should contain:

```json
{
  "tutors": [
    {
      "telegram_id": "123456789",
      "name": "John Doe",
      "sheets_id": "1ABC2DEF3GHI4JKL5MNO6PQR7STU8VWX9YZ",
      "created_at": "2024-01-15T10:30:45.123456",
      "updated_at": "2024-01-15T10:30:45.123456"
    }
  ]
}
```

---

## Verification Checklist

After implementing and testing, verify:

- [ ] `/start` differentiates registered and new users
- [ ] `/register` validates sheet URLs/IDs
- [ ] `/register` prevents duplicate registrations
- [ ] `/register` creates required worksheets
- [ ] `/profile` displays correct information for registered users
- [ ] `/profile` shows error for unregistered users
- [ ] `/help` displays all commands
- [ ] Error messages are user-friendly and helpful
- [ ] Invalid inputs are handled gracefully
- [ ] Registration can be cancelled with `/cancel`
- [ ] Worksheets are pre-created during registration

---

## Notes

- All messages are in Russian (can be customized in `utils/messages.py`)
- Timestamps are stored in ISO format in `tutors_config.json`
- Sheet IDs must be at least 11 characters long to be considered valid
- Names must be 2-100 characters and can contain letters, digits, spaces, hyphens, and apostrophes
