import csv
import io
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, Response, jsonify, request, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
CORS(app, supports_credentials=True)

# Configure cookies dynamically for local development vs production deployment on Render
if os.environ.get("RENDER"):
    app.config.update(
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True,
    )
else:
    app.config.update(
        SESSION_COOKIE_SAMESITE='Lax',
    )

DB_PATH = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                rating INTEGER,
                comments TEXT,
                date_submitted TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
            """
        )

# Initialize database tables on app startup
init_db()


@app.route("/api/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.json or request.form
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    comments = data.get("comments", "").strip()

    try:
        rating = int(data.get("rating", 0))
    except ValueError:
        return jsonify({"error": "Invalid rating"}), 400

    if not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    submitted_at = datetime.now().isoformat(timespec="seconds")

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO feedback(name, email, rating, comments, date_submitted)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, rating, comments, submitted_at),
        )

    return jsonify({"message": "Feedback submitted successfully"}), 201


@app.route("/api/delete/<int:id>", methods=["DELETE"])
def delete_feedback(id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    conn.execute("DELETE FROM feedback WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Feedback deleted successfully"})


@app.route("/api/admin-dashboard", methods=["GET"])
def admin():
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401

    with get_db_connection() as conn:
        data = conn.execute("SELECT * FROM feedback ORDER BY id ASC").fetchall()
        avg = conn.execute("SELECT AVG(rating) FROM feedback").fetchone()[0] or 0
        total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]

    return jsonify({
        "data": [dict(row) for row in data],
        "avg": avg,
        "total": total
    })


@app.route("/api/export-csv", methods=["GET"])
def export_csv():
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401

    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, rating, comments, date_submitted FROM feedback ORDER BY id ASC"
        ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "rating", "comments", "date_submitted"])
    for row in rows:
        writer.writerow([row["id"], row["name"], row["email"], row["rating"], row["comments"], row["date_submitted"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=feedback.csv"},
    )


@app.route("/api/feedback", methods=["GET"])
def api_feedback():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, rating, comments, date_submitted FROM feedback ORDER BY id ASC"
        ).fetchall()

    payload = [dict(row) for row in rows]
    return jsonify(payload)


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or request.form
    username = data.get("username", "")
    password = data.get("password", "")

    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if user and check_password_hash(user["password"], password):
        session["is_admin"] = True
        session["user_id"] = user["id"]
        return jsonify({"message": "Logged in successfully", "username": username})

    return jsonify({"error": "Invalid username or password"}), 401


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json or request.form
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    with get_db_connection() as conn:
        existing = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            return jsonify({"error": "Username already exists"}), 400

        hashed_pw = generate_password_hash(password)
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))

    return jsonify({"message": "User created successfully"}), 201


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@app.route("/api/session", methods=["GET"])
def check_session():
    if session.get("is_admin"):
        return jsonify({"is_admin": True})
    return jsonify({"is_admin": False})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
