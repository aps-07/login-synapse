from flask import Flask, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)


app.secret_key = os.environ.get("SECRET-KEY")

DATABASE = os.path.join(app.root_path, "users.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK(role IN ('admin', 'user'))
            )
        """)

        accounts = [
            ("admin@example.com", "123456", "admin"),
            ("user@example.com", "123456", "user")
        ]

        for email, password, role in accounts:
            exists = conn.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,)
            ).fetchone()

            if exists is None:
                conn.execute(
                    """
                    INSERT INTO users (email, password_hash, role)
                    VALUES (?, ?, ?)
                    """,
                    (
                        email,
                        generate_password_hash(password),
                        role
                    )
                )


# Authentication decorator
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please log in"}), 401

        return function(*args, **kwargs)

    return wrapper


# Admin-only authorization decorator
def admin_required(function):
    @wraps(function)
    @login_required
    def wrapper(*args, **kwargs):
        with get_db() as conn:
            user = conn.execute(
                "SELECT role FROM users WHERE id = ?",
                (session["user_id"],)
            ).fetchone()

        if user is None or user["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return function(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    return render_template("index.html")


# Login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not isinstance(password, str) or not password:
        return jsonify({
            "error": "Enter your email and password"
        }), 400

    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    session.clear()
    session["user_id"] = user["id"]

    return jsonify({
        "message": "Login successful",
        "email": user["email"],
        "role": user["role"]
    })


# Restore current session
@app.route("/api/me", methods=["GET"])
@login_required
def current_user():
    with get_db() as conn:
        user = conn.execute(
            "SELECT email, role FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

    if user is None:
        session.clear()
        return jsonify({"error": "Account not found"}), 401

    return jsonify({
        "email": user["email"],
        "role": user["role"]
    })


# Admin-only: view registered accounts
@app.route("/api/admin/users", methods=["GET"])
@admin_required
def list_users():
    with get_db() as conn:
        users = conn.execute(
            "SELECT id, email, role FROM users ORDER BY id"
        ).fetchall()

    return jsonify({
        "users": [dict(user) for user in users]
    })


# Logout
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


if __name__ == "__main__":
    initialize_db()
    print("App location:", app.root_path)
    print("Template folder:", app.template_folder)
    app.run(debug=True)