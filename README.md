# Preschool Management System

A web-based Preschool Management System built using **Flask**, **MySQL**, and **Bootstrap**. The application provides separate portals for **Administrators**, **Teachers**, and **Parents** to efficiently manage preschool operations.

## Features

- Role-based authentication (Admin, Teacher, Parent)
- Student and Teacher Management
- Parent Registration & Approval
- Attendance Management
- Timetable Management
- Event Management
- Fee Management
- Secure password hashing using Werkzeug

---

## Tech Stack

- Python
- Flask
- MySQL
- HTML/CSS
- Bootstrap 5
- Jinja2

---

## Project Structure

```
Preschool-Management-System/
│
├── app.py
├── db.py
├── routes/
├── templates/
├── static/
└── preschool_db/
    └── preschool_db.sql
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/neha-436/Preschool.git
cd Preschool
```

### 2. Create a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is unavailable:

```bash
pip install Flask mysql-connector-python
```

### 4. Import the database

Use any MySQL user with permission to create databases and run:

```bash
mysql -u <mysql_username> -p < preschool_db/preschool_db.sql
```

This SQL script automatically:
- Creates the `flaskapp` database
- Creates all required tables
- Inserts a default administrator account

### 5. Configure the database

Update the MySQL credentials in `db.py`.

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "<mysql_username>"
MYSQL_PASSWORD = "<mysql_password>"
MYSQL_DB = "flaskapp"
```

### 6. Run the application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## Default Admin

The SQL script inserts a default administrator account. Update the credentials below according to your SQL file.

| Email | Password |
|-------|----------|
| `admin@gmail` | `admin123` |

> Passwords are securely stored as hashed values.

---

## License

This project was developed for educational purposes.
