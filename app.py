import os
import sqlite3
from datetime import date
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "expense_portal.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-development-key")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_db() as connection:
        with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as schema_file:
            schema = schema_file.read()
        # Keep only table/index definitions during normal startup; sample inserts are optional.
        schema = schema.split("-- Sample data uses")[0]
        connection.executescript(schema)


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)

    return wrapped_view


def selected_range():
    today = date.today().isoformat()
    month_start = date.today().replace(day=1).isoformat()
    from_date = request.args.get("from_date", month_start)
    to_date = request.args.get("to_date", today)
    return from_date, to_date


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if not full_name or not email or len(password) < 6:
            flash("Enter all details. Password must contain at least 6 characters.", "danger")
            return render_template("register.html")
        try:
            with get_db() as connection:
                connection.execute(
                    "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                    (full_name, email, generate_password_hash(password)),
                )
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        with get_db() as connection:
            user = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            return redirect(url_for("home"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    user_id = session["user_id"]
    with get_db() as connection:
        summary = connection.execute(
            """SELECT
                COALESCE(SUM(CASE WHEN transaction_type = 'Received' THEN amount ELSE 0 END), 0) AS total_received,
                COALESCE(SUM(CASE WHEN transaction_type = 'Spend' THEN amount ELSE 0 END), 0) AS total_spent
            FROM transactions WHERE user_id = ?""",
            (user_id,),
        ).fetchone()
        recent = connection.execute(
            """SELECT * FROM transactions WHERE user_id = ?
            ORDER BY transaction_date DESC, transaction_id DESC LIMIT 5""",
            (user_id,),
        ).fetchall()
    balance = summary["total_received"] - summary["total_spent"]
    return render_template("home.html", summary=summary, balance=balance, recent=recent)


@app.route("/transaction/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        transaction_date = request.form["transaction_date"]
        transaction_type = request.form["transaction_type"]
        category = request.form["category"].strip()
        description = request.form["description"].strip()
        try:
            amount = float(request.form["amount"])
            if amount <= 0 or transaction_type not in {"Received", "Spend"} or not category:
                raise ValueError
        except ValueError:
            flash("Enter a valid positive amount, type, and category.", "danger")
            return render_template("add_transaction.html", today=date.today().isoformat())
        with get_db() as connection:
            connection.execute(
                """INSERT INTO transactions
                (user_id, transaction_date, transaction_type, amount, category, description)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (session["user_id"], transaction_date, transaction_type, amount, category, description),
            )
        flash("Transaction saved successfully.", "success")
        return redirect(url_for("home"))
    return render_template("add_transaction.html", today=date.today().isoformat())


@app.route("/dashboard")
@login_required
def dashboard():
    from_date, to_date = selected_range()
    with get_db() as connection:
        summary = connection.execute(
            """SELECT
                COALESCE(SUM(CASE WHEN transaction_type = 'Received' THEN amount ELSE 0 END), 0) AS total_received,
                COALESCE(SUM(CASE WHEN transaction_type = 'Spend' THEN amount ELSE 0 END), 0) AS total_spent
            FROM transactions
            WHERE user_id = ? AND transaction_date BETWEEN ? AND ?""",
            (session["user_id"], from_date, to_date),
        ).fetchone()
        categories = connection.execute(
            """SELECT transaction_type, category, SUM(amount) AS total_amount
            FROM transactions
            WHERE user_id = ? AND transaction_date BETWEEN ? AND ?
            GROUP BY transaction_type, category ORDER BY total_amount DESC""",
            (session["user_id"], from_date, to_date),
        ).fetchall()
    total_received = summary["total_received"]
    total_spent = summary["total_spent"]
    total = total_received + total_spent
    return render_template(
        "dashboard.html", summary=summary, balance=total_received - total_spent,
        spending_percentage=(total_spent / total * 100 if total else 0),
        receiving_percentage=(total_received / total * 100 if total else 0),
        categories=categories, from_date=from_date, to_date=to_date,
    )


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
