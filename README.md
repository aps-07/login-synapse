# Synapse — Role-Based Login & Dashboard

Synapse is a web application that provides authentication and personalized dashboards based on user roles. Built using Flask and SQLite, it allows administrators and regular users to access different interfaces through a single login page.

## Features

* **Role-Based Authentication:** Automatically identifies Admin and User accounts after login.
* **Admin Dashboard:** Provides access to the registered-user list.
* **User Dashboard:** Displays a personalized dashboard for regular users.
* **Secure Password Storage:** Uses password hashing instead of storing passwords as plain text.
* **Session Management:** Maintains login sessions and supports logout.
* **Access Control:** Restricts administrative endpoints to authorized administrators.
* **Responsive UI:** Modern login page and dashboard design that adapts to different screen sizes.

## Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML5, CSS3, JavaScript
* **Database:** SQLite
* **Authentication:** Flask sessions and Werkzeug password hashing

## Project Structure

```text
login-synapse/
├── app.py
├── users.db
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Getting Started

1. Clone the repository:

   ```bash
   git clone YOUR_REPOSITORY_URL
   ```

2. Navigate to the project directory:

   ```bash
   cd "login synapse"
   ```

3. Install Flask:

   ```bash
   python -m pip install flask
   ```

4. Start the application:

   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

The application initializes the SQLite database and creates demo accounts when the database initialization code runs.

## Learning Outcomes

This project demonstrates practical implementation of Flask routing, REST-style API endpoints, frontend-backend communication, SQLite database operations, password hashing, session handling, and role-based authorization.

## Future Improvements

* User registration and account management
* Password reset functionality
* CSRF protection and login rate limiting
* Improved admin user-management tools
* Deployment to a production hosting platform

## Disclaimer

This is a learning project. Before production deployment, configure a strong secret key, disable Flask debug mode, and implement additional security protections.
