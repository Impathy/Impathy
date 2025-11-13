# Bot Commands Documentation

This document describes all available commands for the Telegram tutoring bot.

## Authentication Commands

### /start
Starts the bot and shows welcome message.
- **New users**: Prompts to register
- **Registered users**: Shows welcome with profile and help options

### /register
Registers a new tutor account.
- Prompts for tutor name
- Requests Google Sheets URL or ID
- Pre-creates all required worksheets
- **Usage**: `/register`

### /profile
Displays your registered profile information.
- Shows tutor name, sheet ID, and registration dates
- **Usage**: `/profile`

### /help
Shows available commands reference.
- **Usage**: `/help`

## Student Management Commands

### /add_student
Adds a new student record to your worksheet.

#### With Arguments (Direct)
```
/add_student Parent Name Student Name Cost
```
Example: `/add_student Ivan Petrov Mikhail 500`

This will add a student with:
- Parent: Ivan Petrov
- Student: Mikhail
- Cost: 500

#### Interactive Mode (No Arguments)
```
/add_student
```
The bot will prompt you for:
1. Parent name
2. Student name
3. Lesson cost (in any currency)

#### Features
- ✅ Prevents duplicate entries (same parent/student pair)
- ✅ Case-insensitive duplicate detection
- ✅ Whitespace normalization
- ✅ Confirmation feedback with all details
- ✅ Can cancel with `/cancel` during interactive mode

#### Examples
```
# Direct mode with single-word names
/add_student Maria Sophia 1500

# Direct mode with multi-word names
/add_student John Smith Emma 2000

# Interactive mode
/add_student
[bot asks for parent name]
Maria Garcia
[bot asks for student name]
Elena Garcia
[bot asks for cost]
1200
[bot confirms: ✅ Ученик успешно добавлен!...]
```

### /list_students
Lists all registered students with their lesson costs.

**Features:**
- Numbered list format
- Shows parent name → student name (cost)
- Sorted by addition order
- Shows helpful message if no students yet

**Usage**: `/list_students`

**Output Example:**
```
📚 Список учеников:

1. Ivan Petrov → Mikhail (500)
2. Maria Garcia → Elena (1200)
3. John Smith → Emma (2000)
```

### /delete_student
Deletes a student record from your worksheet.

#### With Arguments (Direct)
```
/delete_student Parent Name Student Name
```
Example: `/delete_student Ivan Petrov Mikhail`

#### Interactive Mode (No Arguments)
```
/delete_student
```
The bot will prompt you for:
1. Parent name
2. Student name
3. Confirmation (must use `/confirm` or `/cancel`)

#### Features
- ✅ Confirmation required before deletion
- ✅ Case-insensitive matching
- ✅ Clear feedback if student not found
- ✅ Shows exactly which record will be deleted

#### Examples
```
# Direct mode with single-word names
/delete_student Maria Sophia

# Direct mode with multi-word names
/delete_student John Smith Emma

# Interactive mode
/delete_student
[bot asks for parent name]
Ivan Petrov
[bot asks for student name]
Mikhail
[bot shows confirmation message]
⚠️ Вы уверены? Это действие нельзя отменить.

Родитель: Ivan Petrov
Ученик: Mikhail

Используйте /confirm для подтверждения или /cancel для отмены.

/confirm
[bot confirms: ✅ Ученик удален!...]
```

## Data Management

All student data is stored in the "Ученики" (Students) worksheet of your Google Sheet with columns:
- **Имя родителя** (Parent Name)
- **Имя ученика** (Student Name)  
- **Стоимость урока** (Lesson Cost)

### Data Consistency Guarantees
- ✅ No duplicate parent/student pairs
- ✅ Case-insensitive duplicate checking
- ✅ Atomic operations (all-or-nothing)
- ✅ Real-time synchronization with Google Sheets

## Error Handling

The bot provides helpful error messages for:
- **Not registered**: Use `/register` first
- **Duplicate student**: Student with same parent already exists
- **Student not found**: No matching record to delete
- **Sheet access issues**: Check sheet sharing and permissions
- **Invalid input**: Follow prompts carefully

## Tips

1. **Multi-word names**: Use quotes or pass as separate arguments
   - Direct: `/add_student "John Smith" "Emma Watson" 2000`
   - Or: `/add_student John Smith Emma Watson 2000`

2. **Case insensitivity**: 
   - Adding "Ivan Petrov" and later "ivan petrov" returns error
   - Deleting works case-insensitively too

3. **Cost format**: Can be any currency format
   - `500`, `1500.50`, `£100`, `$1000`, etc.

4. **Cancellation**: 
   - During any interactive conversation, use `/cancel`
   - During delete confirmation, use `/cancel`

## Usage Flow Example

```
# 1. Start with registration
/start
[follows registration steps]

# 2. Add some students
/add_student
[interactive conversation]

# 3. View your students
/list_students

# 4. Delete if needed
/delete_student Parent Student

# 5. View profile anytime
/profile
```
