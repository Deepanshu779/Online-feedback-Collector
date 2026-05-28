# Online Feedback Collector with Admin Dashboard

## Description
Online Feedback Collector is a web application built with a decoupled architecture. It uses a **Python Flask API** for the backend and a standalone **HTML/CSS/JS** frontend.
Users can submit feedback through a simple, modern form. Administrators (or authorized users) can register, log in, and use the dashboard to view, analyze, and manage the feedback data. 

The application recently underwent a major update to separate the monolithic structure into distinct `frontend` and `backend` directories, featuring a **Premium Dark Theme** UI and enhanced security with **Password Hashing**.

## Features
- **Decoupled Architecture:** Separate backend API and frontend static files communicating via REST.
- **Submit Feedback:** Users can submit their Name, Email, Rating (Star Rating Widget), and Comments.
- **Secure Authentication:** User registration and login backed by `werkzeug.security` for password hashing and standard session cookies.
- **Admin Dashboard:** View all feedback in a structured table.
- **Data Visualizations:** Interactive Bar and Pie charts (via Chart.js) to visualize rating distributions dynamically.
- **Data Management:** Delete individual feedback entries.
- **Export to CSV:** Easily download all collected feedback data as a CSV file.
- **Modern UI:** Responsive, clean, glassmorphic dark theme aesthetic.

## Technologies Used
**Frontend:**
- HTML5, CSS3, Vanilla JavaScript (Fetch API)
- Chart.js (Data Visualization)
- Font Awesome (Icons/Star Ratings)
- Google Fonts (Inter)

**Backend:**
- Python 3
- Flask & Flask-CORS
- Werkzeug (Security/Password Hashing)

**Database:**
- SQLite

## How to Run the Project Locally

Because the frontend and backend are decoupled, you need to run them as two separate services.

### 1. Run the Backend API
Open a terminal and navigate to the `backend` directory:
```bash
cd backend
pip install flask flask-cors werkzeug
python app.py
```
*The backend API will start on `http://localhost:5000`.*

### 2. Run the Frontend Client
Open a second terminal and navigate to the `frontend` directory:
```bash
cd frontend
python -m http.server 8000
```
*The frontend application will be served on `http://localhost:8000`.*

### 3. Open in Browser
Navigate to `http://localhost:8000/index.html` to access the application.

## Account Setup & Login

To access the dashboard:
1. Ensure both the frontend and backend servers are running.
2. Navigate to `http://localhost:8000/signup.html`.
3. Create a new user account.
4. Log in with your new credentials to access the Admin Dashboard.

## API Endpoints
- `POST /api/submit-feedback` - Submits a new feedback entry.
- `POST /api/login` - Authenticates a user.
- `POST /api/signup` - Registers a new user.
- `GET /api/admin-dashboard` - Returns feedback stats and data for the dashboard.
- `GET /api/export-csv` - Returns a CSV file of feedback data.
- `DELETE /api/delete/<id>` - Deletes a specific feedback entry.

## Author
**Deepanshu Kumar Pandit**  
B.Tech CSE (Artificial Intelligence)  
Greater Noida Institute of Technology