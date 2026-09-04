# Feedback Collector

A modern full-stack feedback platform with a public feedback form and a protected admin dashboard. The project uses a lightweight Flask REST API, SQLite persistence, and a responsive vanilla HTML/CSS/JavaScript frontend.

## ✨ Highlights

- Clean, responsive feedback experience with 1–5 star rating
- Client + server-side validation for names, email, rating, and comments
- Secure admin signup/login using Werkzeug password hashing
- HttpOnly session cookies with production-aware cookie settings
- Admin dashboard with total responses, average rating, 5-star count, and today's responses
- Search and rating filters for feedback
- Interactive Chart.js rating distribution
- CSV export for admin reporting
- Safe DOM rendering of feedback content to reduce XSS risk
- Health-check endpoint for deployment monitoring
- SQLite path configured relative to the backend or through `DB_PATH`
- Local SQLite database files are ignored by Git

## 🧱 Project Structure

```text
Online-feedback-Collector/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── admin.html
│   └── static/
│       └── css/
│           └── style.css
└── README.md
```

## 🛠️ Tech Stack

**Frontend**
- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js
- Font Awesome
- Inter

**Backend**
- Python 3
- Flask
- Flask-CORS
- Werkzeug
- Gunicorn

**Database**
- SQLite

## 🚀 Run Locally

### 1. Start the API

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set a strong secret:

Windows PowerShell:

```powershell
$env:SECRET_KEY="replace-with-a-random-secret"
```

macOS/Linux:

```bash
export SECRET_KEY="replace-with-a-random-secret"
```

Start Flask:

```bash
python app.py
```

The API runs on `http://localhost:5000`.

### 2. Open the frontend

Serve the `frontend` folder with any static server. For example:

```bash
cd frontend
python -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

The frontend uses same-origin API paths by default, so for a separately hosted frontend you can add a global `window.__FEEDBACK_API__` value before the page scripts load.

## 🔐 Environment Variables

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Flask session signing key | `long-random-secret` |
| `DB_PATH` | Optional SQLite file location | `/var/data/feedback.db` |
| `PORT` | Server port | `5000` |
| `RENDER` | Enables production cookie settings | `true` |
| `FLASK_DEBUG` | Enables Flask debug mode only when set to `1` | `1` |

For production, always provide a strong `SECRET_KEY` and use HTTPS.

## 📡 API

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/health` | Public | Health check |
| `POST` | `/api/submit-feedback` | Public | Submit feedback |
| `POST` | `/api/signup` | Public | Create admin account |
| `POST` | `/api/login` | Public | Log in |
| `POST` | `/api/logout` | Session | Log out |
| `GET` | `/api/session` | Session | Check current session |
| `GET` | `/api/admin-dashboard` | Admin | Fetch stats + feedback |
| `GET` | `/api/export-csv` | Admin | Export feedback CSV |
| `DELETE` | `/api/delete/<id>` | Admin | Delete feedback |

## ☁️ Deployment Notes

For a split deployment, host the static frontend on a service such as Vercel and the Flask API on a Python-compatible service such as Render.

For a cross-origin production setup, configure the frontend API base URL to your backend URL and restrict CORS to your real frontend origin rather than allowing every origin.

For persistent production data, use a persistent disk/volume for SQLite or move the database to a managed relational database.

## 👤 Author

**Deepanshu Kumar Pandit**  
B.Tech CSE (Artificial Intelligence)  
Greater Noida Institute of Technology
