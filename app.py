from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "change-this-to-something-secret"
Session(app)

DB = "finance.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income','expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                date TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)

@app.route("/")
@login_required
def index():
    db = get_db()
    uid = session["user_id"]
    rows = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 5", (uid,)
    ).fetchall()
    totals = db.execute("""
        SELECT
            SUM(CASE WHEN type='income'  THEN amount ELSE 0 END) AS income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expenses
        FROM transactions WHERE user_id = ?
    """, (uid,)).fetchone()
    income   = totals["income"]   or 0
    expenses = totals["expenses"] or 0
    balance  = income - expenses
    return render_template("index.html",
        transactions=rows, income=income,
        expenses=expenses, balance=balance,
        username=session["username"]
    )

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    categories = {
        "income":  ["Salary", "Freelance", "Gift", "Other"],
        "expense": ["Food", "Rent", "Transport", "Entertainment", "Health", "Other"]
    }
    if request.method == "POST":
        t_type   = request.form.get("type")
        category = request.form.get("category")
        amount   = request.form.get("amount")
        note     = request.form.get("note", "")
        date     = request.form.get("date") or datetime.today().strftime("%Y-%m-%d")
        if not t_type or not category or not amount:
            flash("Please fill in all required fields.", "error")
            return render_template("add.html", categories=categories)
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "error")
            return render_template("add.html", categories=categories)
        db = get_db()
        db.execute(
            "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?,?,?,?,?,?)",
            (session["user_id"], t_type, category, amount, note, date)
        )
        db.commit()
        flash("Transaction added!", "success")
        return redirect("/")
    return render_template("add.html", categories=categories)

@app.route("/history")
@login_required
def history():
    db  = get_db()
    uid = session["user_id"]
    filter_type = request.args.get("type", "all")
    filter_cat  = request.args.get("category", "all")
    query  = "SELECT * FROM transactions WHERE user_id = ?"
    params = [uid]
    if filter_type != "all":
        query += " AND type = ?"
        params.append(filter_type)
    if filter_cat != "all":
        query += " AND category = ?"
        params.append(filter_cat)
    query += " ORDER BY date DESC"
    rows = db.execute(query, params).fetchall()
    cats = db.execute(
        "SELECT DISTINCT category FROM transactions WHERE user_id = ?", (uid,)
    ).fetchall()
    return render_template("history.html",
        transactions=rows,
        categories=[r["category"] for r in cats],
        filter_type=filter_type,
        filter_cat=filter_cat
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")
        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("Username already taken.", "error")
            return render_template("register.html")
        flash("Account created! Please log in.", "success")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)