# 💰 Spendly — Personal Finance Tracker

A full stack web application for tracking personal income and expenses, built with Python, Flask, and SQLite.

---

## 🛠️ Tech Stack

**Frontend**
- HTML5 & Jinja2 templates
- CSS3 (custom design system, dark theme)
- Vanilla JavaScript (dynamic form behaviour)

**Backend**
- Python 3
- Flask (routing, sessions, flash messages)
- Werkzeug (password hashing)
- Flask-Session (server-side session management)

**Database**
- SQLite3 (via Python's built-in `sqlite3` module)

---

## ✨ Features

- 🔐 User authentication — register, login, logout with hashed passwords
- ➕ Add income and expense transactions with categories, dates, and notes
- 📊 Dashboard showing balance, total income, total expenses, and spending by category
- 📋 Full transaction history with filtering by type and category
- 🗑️ Delete transactions
- 📱 Responsive layout

---

## 🚀 Getting Started

### Prerequisites
- Python 3 installed on your machine

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/YOUR_USERNAME/finance-tracker.git
   cd finance-tracker
   ```

2. Install dependencies
   ```bash
   pip3 install -r requirements.txt
   ```

3. Run the app
   ```bash
   python3 app.py
   ```

4. Open your browser and go to
   ```
   http://127.0.0.1:5000
   ```

---

## 📁 Project Structure

```
finance-tracker/
├── app.py                  # Flask app — routes, logic, database
├── finance.db              # SQLite database (auto-created on first run)
├── requirements.txt        # Python dependencies
├── static/
│   └── styles.css          # All styling
└── templates/
    ├── layout.html         # Base template (nav, flash messages)
    ├── index.html          # Dashboard
    ├── add.html            # Add transaction form
    ├── history.html        # Transaction history
    ├── login.html          # Login page
    └── register.html       # Register page
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE transactions (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL,
    type     TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount   REAL NOT NULL,
    note     TEXT,
    date     TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

---

## 🎓 Built As Part Of

This project was built as a follow-on to completing [CS50x](https://cs50.harvard.edu/x/) — Harvard's Introduction to Computer Science. It applies concepts from the course including Flask, SQL, Python, and web development.

---

## 📌 Planned Features

- [ ] Export transactions to CSV
- [ ] Monthly budget goals per category
- [ ] Charts using Chart.js
- [ ] Deploy to the web (Render / Railway)
