import csv
import io
import os
import sqlite3
from datetime import datetime

from flask import Flask, Response, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

DB_PATH = "database.db"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    comments = request.form.get("comments", "").strip()

    try:
        rating = int(request.form.get("rating", 0))
    except ValueError:
        return "Invalid rating", 400

    if not (1 <= rating <= 5):
        return "Rating must be between 1 and 5", 400

    if not name or not email:
        return "Name and email are required", 400

    submitted_at = datetime.now().isoformat(timespec="seconds")

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO feedback(name, email, rating, comments, date_submitted)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, rating, comments, submitted_at),
        )

    return redirect("/")

@app.route("/delete/<int:id>")
def delete_feedback(id):

    if not session.get("is_admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM feedback WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

@app.route("/admin-dashboard")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    with get_db_connection() as conn:
        data = conn.execute("SELECT * FROM feedback ORDER BY id ASC").fetchall()
        avg = conn.execute("SELECT AVG(rating) FROM feedback").fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]

    return render_template("admin.html", data=data, avg=avg, total=total)


@app.route("/export-csv")
def export_csv():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

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


@app.route("/api/feedback")
def api_feedback():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, rating, comments, date_submitted FROM feedback ORDER BY id ASC"
        ).fetchall()

    payload = [dict(row) for row in rows]
    return jsonify(payload)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
