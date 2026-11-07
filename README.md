#Multi Task Student Management — Flask + SQLite

This single workspace includes the six task areas described in the internship PDF:
1. Student Management: create, view, search, update, delete.
2. Library Management: book CRUD, issue/return, transaction history.
3. Inventory Management: inventory CRUD and search.
4. Employee Management: employee CRUD and search.
5. Online Examination: question bank, exam taking, automatic score, results.
6. Task Management: create, view, search, update, delete tasks.

## Windows / VS Code setup
1. Install Python 3.11 or newer.
2. Extract this ZIP and open the extracted folder in VS Code.
3. Open Terminal → New Terminal.
4. Run these commands one at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, switch the VS Code terminal to Command Prompt and run:

```bat
.venv\\Scripts\\activate.bat
```

5. Open http://127.0.0.1:5000 in your browser. The `internship.db` SQLite file is created on first run.

## Testing checklist
- Student module: add a student, search, edit, and delete.
- Library: add a book with copies > 0, issue it (copy count falls), return it (count rises), view Library History.
- Inventory: add an item, search by name/SKU, edit quantity.
- Employee: add, search, edit, delete.
- Exam: add questions in Question Bank; take the exam; verify score in Exam Results.
- Task manager: add a task, update status, search, delete.

## Notes
This is an internship demonstration project, not production software. The app uses parameterized SQL values and Flask template escaping. Change the secret key before deployment. Keep screenshots of the dashboard and each module for your internship submission.

<img width="1897" height="853" alt="Screenshot 2026-11-07 125458" src="https://github.com/user-attachments/assets/9c3bb080-81b6-4fa9-af2b-aa279432ed13" />
<img width="1908" height="858" alt="Screenshot 2026-11-07 125419" src="https://github.com/user-attachments/assets/4f7d6849-8f2e-4080-b684-8bbd3963d47c" />
<img width="1912" height="853" alt="Screenshot 2026-11-07 125355" src="https://github.com/user-attachments/assets/9cc17f23-164d-4a78-93e4-1032004aaebc" />
<img width="1907" height="857" alt="Screenshot 2026-11-07 125325" src="https://github.com/user-attachments/assets/f65c27ca-74c2-4a65-a5a2-a7d80d6c0e24" />
