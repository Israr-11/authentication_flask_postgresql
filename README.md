# Authentication & Authorization with Flask and PostgreSQL

This project demonstrates a basic authentication and authorization system built with **Flask**, **PostgreSQL**, and **JWT**.
It includes:

* User registration with email validation and password hashing (bcrypt).
* Secure login that returns **access** and **refresh tokens** using `Flask-JWT-Extended`.
* Token refresh endpoint to issue new access tokens.
* Role-based authorization (extendable for admin/user).

### Tech Stack

* Python (Flask)
* PostgreSQL (with SQLAlchemy ORM)
* Flask-JWT-Extended
* Bcrypt for password hashing
* Email-validator for email verification

### Setup

```bash
# Clone the repo
git clone https://github.com/Israr-11/authentication_flask_postgresql.git
cd authentication_flask_postgresql
```


# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate   # (Windows PowerShell)

# Install dependencies
pip install -r requirements.txt

# Run the app
flask --app app run --debug
```

---
