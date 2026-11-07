from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "replace-this-key-before-deployment"
DB = os.path.join(os.path.dirname(__file__), "internship.db")

MODULES = {
 "students": ("Student Management", [("name","Full name"),("email","Email"),("course","Course"),("year","Year")], ["name","email","course"]),
 "books": ("Library Management", [("title","Book title"),("author","Author"),("isbn","ISBN"),("copies","Available copies")], ["title","author","isbn"]),
 "inventory": ("Inventory Management", [("name","Item name"),("sku","SKU"),("quantity","Quantity"),("price","Unit price")], ["name","sku"]),
 "employees": ("Employee Management", [("name","Full name"),("email","Email"),("department","Department"),("role","Job role")], ["name","email","department"]),
 "questions": ("Online Examination - Question Bank", [("question","Question"),("option_a","Option A"),("option_b","Option B"),("option_c","Option C"),("option_d","Option D"),("correct","Correct option A/B/C/D")], ["question"]),
 "tasks": ("Task Management", [("title","Task title"),("description","Description"),("due_date","Due date YYYY-MM-DD"),("status","Status Pending/In Progress/Completed")], ["title","description","status"])
}

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        for table, (_, fields, _) in MODULES.items():
            cols = ", ".join(f'"{key}" TEXT' for key, label in fields)
            con.execute(f'CREATE TABLE IF NOT EXISTS "{table}" (id INTEGER PRIMARY KEY AUTOINCREMENT, {cols}, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        con.execute("""CREATE TABLE IF NOT EXISTS book_transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER, student_name TEXT,
            action TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("""CREATE TABLE IF NOT EXISTS exam_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, score INTEGER,
            total INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

@app.route("/")
def home():
    with connect() as con:
        counts = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in MODULES}
    return render_template("home.html", modules=MODULES, counts=counts)

@app.route("/<table>")
def listing(table):
    if table not in MODULES: return "Page not found", 404
    title, fields, searchable = MODULES[table]
    q = request.args.get("q", "").strip()
    with connect() as con:
        if q:
            clause = " OR ".join(f'"{field}" LIKE ?' for field in searchable)
            rows = con.execute(f'SELECT * FROM "{table}" WHERE {clause} ORDER BY id DESC', [f"%{q}%"]*len(searchable)).fetchall()
        else:
            rows = con.execute(f'SELECT * FROM "{table}" ORDER BY id DESC').fetchall()
        books = con.execute("SELECT id,title,copies FROM books ORDER BY title").fetchall() if table == "books" else []
    return render_template("list.html", table=table, title=title, fields=fields, rows=rows, q=q, books=books)

@app.route("/<table>/add", methods=["GET","POST"])
@app.route("/<table>/edit/<int:record_id>", methods=["GET","POST"])
def edit_record(table, record_id=None):
    if table not in MODULES: return "Page not found", 404
    title, fields, searchable = MODULES[table]
    with connect() as con:
        record = con.execute(f'SELECT * FROM "{table}" WHERE id=?', (record_id,)).fetchone() if record_id else None
        if record_id and not record: return "Record not found", 404
        if request.method == "POST":
            values = [request.form.get(k, "").strip() for k, label in fields]
            if not all(values):
                flash("Please complete all fields.", "error")
            elif table == "questions" and values[-1].upper() not in ("A","B","C","D"):
                flash("Correct answer must be A, B, C, or D.", "error")
            else:
                if record_id:
                    sets = ", ".join(f'"{k}"=?' for k, label in fields)
                    con.execute(f'UPDATE "{table}" SET {sets} WHERE id=?', values + [record_id])
                    flash("Updated successfully.")
                else:
                    cols = ", ".join(f'"{k}"' for k, label in fields)
                    marks = ", ".join("?" for _ in values)
                    con.execute(f'INSERT INTO "{table}" ({cols}) VALUES ({marks})', values)
                    flash("Added successfully.")
                con.commit()
                return redirect(url_for("listing", table=table))
    return render_template("form.html", table=table, title=title, fields=fields, record=record)

@app.route("/<table>/delete/<int:record_id>", methods=["POST"])
def delete_record(table, record_id):
    if table not in MODULES: return "Page not found", 404
    with connect() as con:
        con.execute(f'DELETE FROM "{table}" WHERE id=?', (record_id,))
        con.commit()
    flash("Record deleted.")
    return redirect(url_for("listing", table=table))

@app.route("/library/action", methods=["POST"])
def library_action():
    book_id = request.form.get("book_id", type=int)
    borrower = request.form.get("student_name", "").strip()
    action = request.form.get("action")
    if not book_id or not borrower or action not in ("Issue", "Return"):
        flash("Select a book, enter borrower name, and choose action.", "error")
        return redirect(url_for("listing", table="books"))
    with connect() as con:
        book = con.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            flash("Book not found.", "error")
        else:
            copies = int(book["copies"] or 0)
            if action == "Issue" and copies <= 0:
                flash("No copies available.", "error")
            else:
                copies += -1 if action == "Issue" else 1
                con.execute("UPDATE books SET copies=? WHERE id=?", (str(copies), book_id))
                con.execute("INSERT INTO book_transactions(book_id,student_name,action) VALUES(?,?,?)", (book_id, borrower, action))
                con.commit()
                flash(f"Book {action.lower()} successful.")
    return redirect(url_for("listing", table="books"))

@app.route("/library/transactions")
def library_transactions():
    with connect() as con:
        rows = con.execute("SELECT bt.*, b.title FROM book_transactions bt LEFT JOIN books b ON b.id=bt.book_id ORDER BY bt.id DESC").fetchall()
    return render_template("transactions.html", rows=rows)

@app.route("/exam/take", methods=["GET","POST"])
def take_exam():
    with connect() as con:
        questions = con.execute("SELECT * FROM questions ORDER BY id").fetchall()
    if request.method == "POST":
        name = request.form.get("student_name", "").strip() or "Guest"
        score = sum(1 for q in questions if request.form.get(str(q["id"]), "").upper() == q["correct"].upper())
        with connect() as con:
            con.execute("INSERT INTO exam_results(student_name,score,total) VALUES(?,?,?)", (name, score, len(questions)))
            con.commit()
        return render_template("result.html", name=name, score=score, total=len(questions))
    return render_template("exam.html", questions=questions)

@app.route("/exam/results")
def exam_results():
    with connect() as con:
        rows = con.execute("SELECT * FROM exam_results ORDER BY id DESC").fetchall()
    return render_template("results.html", rows=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
