# Online Feedback Collector with Admin Dashboard

## Description
Online Feedback Collector is a web application built using Python, Flask, and SQLite.  
Users can submit feedback through a simple, modern form. Administrators (or authorized users) can register, log in, and use the dashboard to view, analyze, and manage the feedback data. 

The application recently underwent a major update to feature a **Clean, Minimalist Corporate UI** and enhanced security with **Password Hashing**.

## Features
- **Submit Feedback:** Users can submit their Name, Email, Rating (Star Rating Widget), and Comments.
- **Secure Authentication:** User registration (`/signup`) and login (`/login`) backed by `werkzeug.security` for password hashing.
- **Admin Dashboard:** View all feedback in a structured, paginated table.
- **Data Visualizations:** Interactive Bar and Pie charts (via Chart.js) to visualize rating distributions.
- **Data Management:** Delete individual feedback entries.
- **Export to CSV:** Easily download all collected feedback data as a CSV file.
- **REST API:** Endpoint (`/api/feedback`) for accessing feedback data programmatically.
- **Modern UI:** Responsive, clean, high-contrast corporate aesthetic.

## Technologies Used
**Frontend:**
- HTML5, CSS3, JavaScript
- Chart.js (Data Visualization)
- Font Awesome (Icons/Star Ratings)

**Backend:**
- Python 3
- Flask
- Werkzeug (Security/Password Hashing)

**Database:**
- SQLite

## How to Run the Project Locally

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the Application:**
```bash
python app.py
```

3. **Open in Browser:**
Navigate to `http://127.0.0.1:5000`

## Account Setup & Login

*Note: The previous hardcoded admin credentials have been removed for security purposes.*

To access the dashboard:
1. Start the application.
2. Navigate to `http://127.0.0.1:5000/signup`.
3. Create a new user account.
4. Log in with your new credentials to access the Admin Dashboard.



## API Endpoint
`/api/feedback` - Returns a JSON payload of all submitted feedback.

## Author
**Deepanshu Kumar Pandit**  
B.Tech CSE (Artificial Intelligence)  
Greater Noida Institute of Technology
