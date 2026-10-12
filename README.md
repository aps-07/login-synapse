# Synapse — Role-Based Login & Dashboard System

Synapse is a web application built with **Python, Flask, SQLite, HTML, CSS, and JavaScript**. It provides a login system with role-based dashboards for Admins, Managers, and regular Users.

The project demonstrates authentication, session management, database integration, and role-based access control.

## Features

* **User Authentication:** Login and logout functionality.
* **Role-Based Dashboards:** Different dashboard experiences for Admins, Managers, and Users.
* **Admin Dashboard:** Access to the registered-user directory and administrative features.
* **Manager Dashboard:** View registered users, including their roles, without admin-only permissions.
* **User Dashboard:** A dedicated dashboard for regular users.
* **Protected API Routes:** Backend authorization to restrict access according to user roles.
* **SQLite Database:** Stores user account information.
* **Responsive Interface:** Frontend built with HTML, CSS, and JavaScript.
* **Cloud Deployment:** Configured for deployment using Render.

## Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite
* **Deployment:** Render
* **Version Control:** Git and GitHub

## Project Structure

```text
login-synapse/
├── app.py
├── requirements.txt
├── users.db
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## User Roles and Permissions

| Feature                    | Admin | Manager | User |
| -------------------------- | ----- | ------- | ---- |
| Login and logout           | Yes   | Yes     | Yes  |
| View registered users      | Yes   | Yes     | No   |
| Access admin-only controls | Yes   | No      | No   |
| Access regular dashboard   | No    | No      | Yes  |

*Actual permissions depend on the backend routes and features implemented in the application.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/aps-07/login-synapse.git
cd login-synapse
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the secret key

Set a secret key in PowerShell before running the application:

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

Keep the secret key private. Never commit it to GitHub.

### 5. Run the application

```bash
python app.py
```

Open the application in your browser:

`http://127.0.0.1:5000`

## Deployment on Render

Synapse can be deployed as a Python web service on Render.

* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn app:app`
* **Environment Variable:** Configure the secret key in the Render Environment settings.

After pushing code changes to GitHub, trigger a deployment on Render or wait for automatic deployment if enabled.

## Security Notes

* Passwords should be stored as secure hashes rather than plain text.
* Protected API endpoints must enforce authorization on the server.
* Secret keys and other sensitive credentials should not be committed to the repository.
* The included SQLite database may contain local development or demonstration data; do not publish real user credentials or private data.

## Future Improvements

* User registration and profile management.
* Password reset functionality.
* Enhanced admin management controls.
* Improved input validation and error handling.
* Production database integration.
* Automated testing for authentication and authorization.

## Author

**Aayush Pratap Singh**

GitHub: [aps-07](https://github.com/aps-07)

---

*Synapse — A role-based authentication and dashboard application built as a web development project.*
