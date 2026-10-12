
import os
import sqlite3
from functools import wraps

from flask import Flask, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Supports both the existing Render variable and the standard name.

app.secret_key = (
    os.environ.get("SECRET_KEY")
    or os.environ.get("SECRET-KEY")
)

if not app.secret_key:
    raise RuntimeError(
        "Set SECRET_KEY or SECRET-KEY in your environment before starting Synapse."
    )

DATABASE = os.path.join(app.root_path, "users.db")


# -------------------- DATABASE --------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Create or migrate the users table and add demo accounts."""

    with get_db() as conn:
        table = conn.execute("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table' AND name = 'users'
        """).fetchone()

        if table is None:
            # Fresh database
            conn.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                        CHECK(role IN ('admin', 'manager', 'user'))
                )
            """)

        elif "'manager'" not in table["sql"]:
            # Migrate the old admin/user-only schema.
            # Existing IDs, emails, password hashes and roles are preserved.
            conn.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                        CHECK(role IN ('admin', 'manager', 'user'))
                )
            """)

            conn.execute("""
                INSERT INTO users_new (id, email, password_hash, role)
                SELECT id, email, password_hash, role
                FROM users
            """)

            conn.execute("DROP TABLE users")
            conn.execute("ALTER TABLE users_new RENAME TO users")

        # Demo accounts are inserted only when the email does not exist.
        accounts = [
            ("admin@example.com", "123456", "admin"),
            ("manager@example.com", "123456", "manager"),
            ("user@example.com", "123456", "user"),
        ]

        for email, password, role in accounts:
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,)
            ).fetchone()

            if existing is None:
                conn.execute("""
                    INSERT INTO users (email, password_hash, role)
                    VALUES (?, ?, ?)
                """, (
                    email,
                    generate_password_hash(password),
                    role
                ))


# -------------------- AUTHORIZATION --------------------

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please log in"}), 401

        # Confirm the account still exists.
        with get_db() as conn:
            user = conn.execute(
                "SELECT id FROM users WHERE id = ?",
                (session["user_id"],)
            ).fetchone()

        if user is None:
            session.clear()
            return jsonify({"error": "Account not found"}), 401

        return function(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles):
    """Allow access only to authenticated users with an allowed role."""

    def decorator(function):
        @wraps(function)
        @login_required
        def wrapper(*args, **kwargs):
            with get_db() as conn:
                user = conn.execute(
                    "SELECT role FROM users WHERE id = ?",
                    (session["user_id"],)
                ).fetchone()

            if user is None:
                session.clear()
                return jsonify({"error": "Account not found"}), 401

            if user["role"] not in allowed_roles:
                return jsonify({
                    "error": "You do not have permission to access this resource"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator


# Admin-only access
admin_required = role_required("admin")

# Managers can view the user directory, but not admin controls.
manager_required = role_required("manager")


# -------------------- FRONTEND --------------------

@app.route("/")
def home():
    return render_template("index.html")


# -------------------- LOGIN --------------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "")
    password = data.get("password", "")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "error": "Enter your email and password"
        }), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "error": "Enter your email and password"
        }), 400

    with get_db() as conn:
        user = conn.execute(
            "SELECT id, email, password_hash, role "
            "FROM users WHERE email = ?",
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


# -------------------- CURRENT SESSION --------------------

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


# -------------------- ADMIN: VIEW ALL USERS --------------------

@app.route("/api/admin/users", methods=["GET"])
@admin_required
def admin_list_users():
    with get_db() as conn:
        users = conn.execute("""
            SELECT id, email, role
            FROM users
            ORDER BY id
        """).fetchall()

    return jsonify({
        "users": [dict(user) for user in users]
    })


# -------------------- MANAGER: READ-ONLY USER DIRECTORY --------------------

@app.route("/api/manager/users", methods=["GET"])
@manager_required
def manager_list_users():
    with get_db() as conn:
        users = conn.execute("""
            SELECT id, email, role
            FROM users
            ORDER BY id
        """).fetchall()

    return jsonify({
        "users": [dict(user) for user in users]
    })


# -------------------- LOGOUT --------------------

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "message": "Logged out successfully"
    })


# Initialize the database when the application starts,
# including when launched through Gunicorn on Render.
initialize_db()


if __name__ == "__main__":
    app.run(debug=True)
