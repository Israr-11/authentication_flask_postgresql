# Authentication and Authorization with Flask and PostgreSQL

This project demonstrates a **complete authentication and authorization system** built with **Flask**, **PostgreSQL**, and **JWT**.
It includes secure user registration, email verification, login with tokens, password reset, and logout.

---

## Complete Authentication Flow

### 1. **User Registration**

* User submits **name, email, password**
* Service validates input and creates a new `User` with `is_verified = False`
* Generates a **verification token** and stores it in the database
* Sends a verification email via **Mailtrap**
* Returns a success response to the client

---

### 2. **Email Verification**

* User clicks the **verification link** received in email
* Server validates the token and marks the user as **verified**
* User can now log in

---

### 3. **Login**

* User submits **email and password**
* Service validates credentials and ensures email is verified
* Generates:

  * **Access token** (stored in **HTTP-only cookie**)
  * **Refresh token** (stored in DB with device info)
* Returns user data and refresh token

---

### 4. **Using Protected Routes**

* Client includes **access token (cookie)** in API requests
* Server validates token and extracts user identity
* If valid, user gains access to protected resources

---

### 5. **Token Refresh**

* When the access token expires, client sends refresh token
* Server validates refresh token against the database
* If valid, issues a new **access token** in an HTTP-only cookie

---

### 6. **Password Reset**

* User requests a password reset by providing email
* Service generates a **reset token** and sends reset link via email
* User clicks link and submits new password
* Service validates token and updates the password (hashed with bcrypt)
* Revokes all existing refresh tokens for that user

---

### 7. **Logout**

* Clears access token cookie
* Revokes refresh token in the database

---

## Security Best Practices Used

* Access tokens stored in **HTTP-only cookies** (safe from JavaScript access)
* Refresh tokens tracked in the **database** (can be revoked anytime)
* Password reset tokens expire quickly (**1 hour**)
* Email verification required before login
* Passwords hashed with **bcrypt + salt**
* Role-based authorization (admin/user) supported

---

## Tech Stack

* **Python (Flask)**
* **PostgreSQL + SQLAlchemy**
* **Flask-JWT-Extended**
* **Bcrypt** for password hashing
* **Mailtrap** for email testing
* **Email-validator** for validation

---

## Setup

```bash
# Clone the repo
git clone https://github.com/Israr-11/authentication_flask_postgresql.git
cd authentication_flask_postgresql

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate   # (Windows PowerShell)

# Install dependencies
pip install -r requirements.txt

# Run the app
flask --app app run --debug
```
