import csv
import io
import os
import re
import sqlite3
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, Response, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "database.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="None" if os.environ.get("RENDER") else "Lax",
    SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER")),
    MAX_CONTENT_LENGTH=64 * 1024,
)
CORS(app, supports_credentials=True)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                comments TEXT DEFAULT '',
                date_submitted TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_date ON feedback(date_submitted)")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        return view(*args, **kwargs)

    return wrapped


def clean_text(value, limit):
    return str(value or "").strip()[:limit]


init_db()


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/submit-feedback")
def submit_feedback():
    data = request.get_json(silent=True) or request.form
    name = clean_text(data.get("name"), 100)
    email = clean_text(data.get("email"), 120).lower()
    comments = clean_text(data.get("comments"), 1000)

    try:
        rating = int(data.get("rating", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Rating must be a number from 1 to 5"}), 400

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Please enter a valid email address"}), 400
    if not 1 <= rating <= 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    submitted_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO feedback(name, email, rating, comments, date_submitted) VALUES (?, ?, ?, ?, ?)",
            (name, email, rating, comments, submitted_at),
        )

    return jsonify({"message": "Feedback submitted successfully"}), 201


@app.delete("/api/delete/<int:feedback_id>")
@admin_required
def delete_feedback(feedback_id):
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Feedback not found"}), 404

    return jsonify({"message": "Feedback deleted successfully"})


@app.get("/api/admin-dashboard")
@admin_required
def admin_dashboard():
    with get_db_connection() as conn:
        data = conn.execute("SELECT * FROM feedback ORDER BY id DESC").fetchall()
        avg = conn.execute("SELECT AVG(rating) FROM feedback").fetchone()[0] or 0
        total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        ratings = conn.execute(
            "SELECT rating, COUNT(*) AS count FROM feedback GROUP BY rating ORDER BY rating"
        ).fetchall()

    return jsonify(
        {
            "data": [dict(row) for row in data],
            "avg": round(float(avg), 2),
            "total": total,
            "ratings": {str(row["rating"]): row["count"] for row in ratings},
        }
    )


@app.get("/api/export-csv")
@admin_required
def export_csv():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, rating, comments, date_submitted FROM feedback ORDER BY id DESC"
        ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "rating", "comments", "date_submitted"])
    writer.writerows(
        [row["id"], row["name"], row["email"], row["rating"], row["comments"], row["date_submitted"]]
        for row in rows
    )

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=feedback.csv"},
    )


@app.get("/api/feedback")
def api_feedback():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, rating, comments, date_submitted FROM feedback ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or request.form
    username = clean_text(data.get("username"), 80)
    password = str(data.get("password") or "")

    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session.clear()
    session["is_admin"] = True
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"message": "Logged in successfully", "username": user["username"]})


@app.post("/api/signup")
def signup():
    data = request.get_json(silent=True) or request.form
    username = clean_text(data.get("username"), 80)
    password = str(data.get("password") or "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409

    return jsonify({"message": "User created successfully"}), 201


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@app.get("/api/session")
def check_session():
    return jsonify(
        {
            "is_admin": bool(session.get("is_admin")),
            "username": session.get("username"),
        }
    )


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
