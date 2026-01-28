# Django Subscription Tracker

A backend-first Django project to learn core Django concepts by building a realistic
subscription and expense tracker. Admin UI is the primary interface for now.

## Table of Contents
- Overview
- Tech Stack
- Setup
- Install Dependencies
- Run the Project
- Admin Login
- Inspect SQLite Data (CLI)
- Project Structure

## Overview
This project tracks recurring subscriptions and one-off expenses. It focuses on:
- clean data models
- admin-driven CRUD
- data integrity
- simple reporting foundations

## Tech Stack
- Python 3.13
- Django 5.2 LTS
- SQLite (local dev)
- uv (package manager / venv)

## Setup
From the project root:

```powershell
uv venv .venv
```

## Install Dependencies
```powershell
uv pip install "Django>=5.2,<5.3"
```

## Run the Project
```powershell
uv run python manage.py migrate
uv run python manage.py runserver
```

Open:
```
http://127.0.0.1:8000/admin
```

## Admin Login
Create a superuser if needed:
```powershell
uv run python manage.py createsuperuser
```

## Inspect SQLite Data (CLI)
Open the database:
```powershell
sqlite3 db.sqlite3
```

Common commands:
```sql
.tables
PRAGMA table_info(subscriptions_expense);
SELECT * FROM subscriptions_expense;
```

## Project Structure
```
config/          Django project settings
subscriptions/   Main app (models + admin)
db.sqlite3       Local SQLite database
```
