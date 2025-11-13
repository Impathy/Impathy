# Student Commands Manual Testing Guide

This document provides step-by-step manual testing scenarios for the student management commands: `/add_student`, `/list_students`, and `/delete_student`.

## Prerequisites

1. Bot is running: `python main.py`
2. A registered tutor with a valid Google Sheet
3. Access to the sheet to verify data persistence

## Test Scenario 1: Adding a New Student (Interactive Mode)

### Steps

1. Start the bot and register a tutor if not already done:
   ```
   /start
   /register
   [Follow registration steps]
   ```

2. Add a student interactively:
   ```
   /add_student
   ```
   
3. Bot responds with:
   ```
   👨‍👩‍👧 Добавление нового ученика
   
   Введите имя родителя:
   ```

4. Enter parent name:
   ```
   Ivan Petrov
   ```

5. Bot responds:
   ```
   Введите имя ученика:
   ```

6. Enter student name:
   ```
   Mikhail Petrov
   ```

7. Bot responds:
   ```
   Введите стоимость урока (в рублях или любой валюте):
   ```

8. Enter lesson cost:
   ```
   1500
   ```

9. Bot confirms with:
   ```
   ✅ Ученик успешно добавлен!
   
   Родитель: Ivan Petrov
   Ученик: Mikhail Petrov
   Стоимость урока: 1500
   ```

### Verification

- ✅ Message shows all entered details
- ✅ Student appears in Google Sheet in "Ученики" worksheet
- ✅ Row contains: "Ivan Petrov", "Mikhail Petrov", "1500"

---

## Test Scenario 2: Adding Students (Direct Mode with Arguments)

### Steps

1. Add a student with all arguments at once:
   ```
   /add_student Maria Garcia Sofia 2000
   ```

2. Bot immediately confirms:
   ```
   ✅ Ученик успешно добавлен!
   
   Родитель: Maria Garcia
   Ученик: Sofia
   Стоимость урока: 2000
   ```

### Verification

- ✅ Multi-word parent name parsed correctly
- ✅ Student added immediately without prompts
- ✅ Data appears in Google Sheet

---

## Test Scenario 3: Adding Multi-Word Names (Direct Mode)

### Steps

1. Add student with multi-word names:
   ```
   /add_student John Smith Emma Watson 1800
   ```

2. Bot confirms:
   ```
   ✅ Ученик успешно добавлен!
   
   Родитель: John Smith
   Ученик: Emma Watson
   Стоимость урока: 1800
   ```

### Verification

- ✅ Multi-word names handled correctly
- ✅ Correct parsing of arguments
- ✅ All names properly stored in sheet

---

## Test Scenario 4: Duplicate Detection (Case-Insensitive)

### Steps

1. Try adding the same student again (different case):
   ```
   /add_student ivan petrov mikhail 500
   ```

2. Bot responds with error:
   ```
   ❌ Ошибка: Ученик с таким родителем уже существует!
   
   Родитель: ivan petrov
   Ученик: mikhail
   ```

### Verification

- ✅ Duplicate detected despite different casing
- ✅ Error message is clear and informative
- ✅ No duplicate row added to sheet

### Steps for Second Duplicate Check

1. Try with extra whitespace:
   ```
   /add_student  Ivan   Petrov    Mikhail  Petrov  999
   ```

2. Bot still detects duplicate:
   ```
   ❌ Ошибка: Ученик с таким родителем уже существует!
   
   Родитель: Ivan Petrov
   Ученик: Mikhail Petrov
   ```

### Verification

- ✅ Whitespace normalized and duplicate still detected
- ✅ Duplicate prevention works reliably

---

## Test Scenario 5: Listing Students

### Steps

1. List all students:
   ```
   /list_students
   ```

2. Bot displays:
   ```
   📚 Список учеников:
   
   1. Ivan Petrov → Mikhail Petrov (1500)
   2. Maria Garcia → Sofia (2000)
   3. John Smith → Emma Watson (1800)
   ```

### Verification

- ✅ All added students appear in the list
- ✅ List is numbered
- ✅ Format shows: Parent → Student (Cost)
- ✅ Students appear in order they were added

---

## Test Scenario 6: Empty Student List

### Steps

1. Delete all students first (see deletion tests)
2. List students:
   ```
   /list_students
   ```

3. Bot responds:
   ```
   📭 У вас пока нет учеников.
   
   Используйте /add_student для добавления нового ученика.
   ```

### Verification

- ✅ Helpful message when no students exist
- ✅ Suggests adding students

---

## Test Scenario 7: Delete Student (Interactive Mode)

### Steps

1. Start deletion:
   ```
   /delete_student
   ```

2. Bot asks:
   ```
   🗑️ Удаление ученика
   
   Введите имя родителя:
   ```

3. Enter parent name:
   ```
   Maria Garcia
   ```

4. Bot asks:
   ```
   Введите имя ученика:
   ```

5. Enter student name:
   ```
   Sofia
   ```

6. Bot shows confirmation:
   ```
   ⚠️ Вы уверены? Это действие нельзя отменить.
   
   Родитель: Maria Garcia
   Ученик: Sofia
   
   Используйте /confirm для подтверждения или /cancel для отмены.
   ```

7. Confirm deletion:
   ```
   /confirm
   ```

8. Bot confirms:
   ```
   ✅ Ученик удален!
   
   Родитель: Maria Garcia
   Ученик: Sofia
   ```

### Verification

- ✅ Confirmation step prevents accidental deletion
- ✅ Student removed from Google Sheet
- ✅ Row with "Maria Garcia" and "Sofia" no longer exists

---

## Test Scenario 8: Delete Student (Direct Mode)

### Steps

1. Delete student with arguments:
   ```
   /delete_student John Smith Emma Watson
   ```

2. Bot immediately confirms:
   ```
   ✅ Ученик удален!
   
   Родитель: John Smith
   Ученик: Emma Watson
   ```

### Verification

- ✅ Direct deletion works without confirmation
- ✅ Student removed from sheet
- ✅ Multi-word names handled correctly

---

## Test Scenario 9: Delete Non-Existing Student

### Steps

1. Try to delete a student that doesn't exist:
   ```
   /delete_student Nonexistent Name Test Student
   ```

2. Bot responds:
   ```
   ❌ Ученик не найден.
   
   Родитель: Nonexistent Name
   Ученик: Test Student
   ```

### Verification

- ✅ Clear error message when student not found
- ✅ No modification to sheet
- ✅ Helpful feedback

---

## Test Scenario 10: Cancel Deletion (Interactive)

### Steps

1. Start deletion:
   ```
   /delete_student
   ```

2. Enter parent name:
   ```
   Ivan Petrov
   ```

3. Enter student name:
   ```
   Mikhail Petrov
   ```

4. At confirmation, cancel:
   ```
   /cancel
   ```

5. Bot responds:
   ```
   ❌ Удаление отменено.
   ```

### Verification

- ✅ Student NOT deleted from sheet
- ✅ Data remains unchanged
- ✅ Cancellation works correctly

---

## Test Scenario 11: Cancel During Add (Interactive)

### Steps

1. Start adding:
   ```
   /add_student
   ```

2. Bot asks for parent name, cancel:
   ```
   /cancel
   ```

3. Bot responds:
   ```
   ❌ Добавление ученика отменено.
   ```

### Verification

- ✅ No student added to sheet
- ✅ Conversation ends gracefully

---

## Test Scenario 12: Not Registered User

### Steps

1. Open new chat (or delete registration)
2. Try to use student commands:
   ```
   /list_students
   ```

3. Bot responds:
   ```
   ❌ Вы не зарегистрированы.
   
   Используйте /register для регистрации.
   ```

### Verification

- ✅ Commands restricted to registered users
- ✅ Helpful error message
- ✅ Suggests registration

---

## Test Scenario 13: Special Characters in Names

### Steps

1. Add student with special characters:
   ```
   /add_student Иванов А. Петр-Сергей 1200
   ```

2. Verify in sheet and list:
   ```
   /list_students
   ```

3. Should show:
   ```
   4. Иванов А. → Петр-Сергей (1200)
   ```

### Verification

- ✅ Russian characters supported
- ✅ Punctuation handled
- ✅ Special characters preserved in sheet

---

## Test Scenario 14: Data Persistence in Google Sheet

### Prerequisites

- Have added several students as per scenarios above

### Steps

1. Open your Google Sheet in a browser
2. Navigate to the "Ученики" worksheet
3. Verify the data:
   - Column A (Имя родителя): Parent names
   - Column B (Имя ученика): Student names
   - Column C (Стоимость урока): Lesson costs

### Verification

- ✅ All student data visible in sheet
- ✅ Correct number of rows (header + students)
- ✅ Data matches what bot reported
- ✅ No extra columns or incorrect data

---

## Test Scenario 15: Help Command Shows New Commands

### Steps

1. Request help:
   ```
   /help
   ```

2. Bot shows all commands including:
   ```
   /add_student - Добавить нового ученика
   /list_students - Список учеников
   /delete_student - Удалить ученика
   ```

### Verification

- ✅ New student commands appear in help
- ✅ Help text is descriptive

---

## Acceptance Criteria Checklist

- [x] `/add_student` command works in interactive mode (prompts for input)
- [x] `/add_student` command works with arguments (direct mode)
- [x] `/list_students` shows all students with parent, student, and cost
- [x] `/delete_student` command works in interactive mode with confirmation
- [x] `/delete_student` command works with arguments
- [x] Duplicate detection works (case-insensitive)
- [x] Duplicate entries are prevented with informative error
- [x] Student records stored in "Ученики" worksheet with correct columns
- [x] Unique constraint enforced per parent/student pair
- [x] Case-insensitive matching for duplicates
- [x] Whitespace normalization works
- [x] Empty list message when no students exist
- [x] Deletion confirmation in interactive mode
- [x] Non-existing student shows clear error
- [x] Cancellation works at all conversation steps
- [x] Commands restricted to registered tutors
- [x] Data persists correctly in Google Sheets
- [x] Multi-word names handled correctly
- [x] Special characters (Russian, punctuation) supported
- [x] All error messages are clear and helpful

---

## Troubleshooting

### Issue: "Вы не зарегистрированы"

**Solution**: Register first with `/register`

### Issue: Duplicate error when adding new student

**Solution**: Check sheet for similar names (case-insensitive). Try different names.

### Issue: "Ученик не найден" when deleting

**Solution**: Use `/list_students` to see exact names, then try deleting again.

### Issue: Student not appearing in list

**Solution**:
1. Check sheet manually for the row
2. Refresh the sheet (F5 in browser)
3. Verify sheet ID matches in `/profile`

### Issue: Sheet access errors

**Solution**:
1. Verify service account email has Editor access to sheet
2. Check sheet is not in trash
3. Verify sheet ID is correct in `/profile`

---

## Notes for Testers

- Each scenario should be tested independently
- Always verify data in Google Sheet
- Test both interactive and direct modes
- Pay attention to whitespace and case handling
- Report any deviations from expected behavior
- Test scenarios can be run in any order (except scenario order within same session matters for persistence tests)
