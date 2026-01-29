# Django Hands-On Notes

This file tracks the commands we ran and why we ran them. We will keep it updated as we progress.

## 1) Project setup

Goal: Create a clean Python environment for this project only.

- Check Python version:
  ```powershell
  python --version
  ```
  Why: Django 5.2 LTS supports Python 3.12 and 3.13. We confirmed Python 3.13.6 is installed.

- Check uv version:
  ```powershell
  uv --version
  ```
  Why: We use uv as the package manager and virtual environment tool.

- Create a project virtual environment:
  ```powershell
  uv venv .venv
  ```
  Why: Isolates dependencies for this project.

- Install Django 5.2 LTS:
  ```powershell
  uv pip install "Django>=5.2,<5.3"
  ```
  Why: Use the LTS version for stability and long support.

## 2) Django project scaffold

Goal: Create the Django project files.

- Create the Django project:
  ```powershell
  uv run django-admin startproject config .
  ```
  Why: Generates `manage.py` and the `config/` settings package in the current folder.

- Create the main app for our features:
  ```powershell
  uv run python manage.py startapp subscriptions
  ```
  Why: We will put our models and admin config for subscriptions here.

- Register the app:
  - File: `config/settings.py`
  - Add `'subscriptions'` to `INSTALLED_APPS`

## 3) Initialize database

Goal: Create Django's built-in tables (admin, auth, sessions).

- Run initial migrations:
  ```powershell
  uv run python manage.py migrate
  ```
  Why: Sets up the default tables so the admin site can work.

## 4) Create admin user

Goal: Create a login for the Django admin site.

- Create a superuser (non-interactive):
  ```powershell
  $env:DJANGO_SUPERUSER_PASSWORD='yubikhadka'; uv run python manage.py createsuperuser --username yubik --email yubik@example.com --noinput
  ```
  Why: The admin site requires a superuser. We used a fixed password for local dev only.

## 5) Core models and admin setup

Goal: Create the Subscription Tracker data model and make it manageable in admin.

- Add models:
  - `Category` (name, user, created_at)
  - `Subscription` (name, category, billing cycle, amount, next renewal, status, etc.)
  - `Expense` (amount, category, date, source, optional subscription, etc.)
  Why: These reflect the core concepts from the PRD.

- Add basic rules:
  - Non-negative amounts
  - Valid billing intervals
  - Subscription-linked expenses must have source = `subscription`
  Why: Keep the data consistent.

- Register models in Django admin and add list filters for quick browsing.
  Why: Admin is our UI for now.

### Model hooks (clean/save)
- `clean()` is a Django model validation hook. Admin calls `full_clean()` which uses this.
- `save()` is called whenever the model is saved; we use it to normalize data.

### Constraint syntax note
We use `CheckConstraint(condition=...)` (instead of `check=`) to be compatible with Django 6+.

## 6) Migrations (create tables)

Goal: Turn our model definitions into real database tables.

- Create migration files:
  ```powershell
  uv run python manage.py makemigrations
  ```
  What it does (simple view):
  - Scans `INSTALLED_APPS` and their `models.py` files.
  - Compares current models with the last migration state.
  - Generates new migration files in `subscriptions/migrations/`.

- Apply migrations:
  ```powershell
  uv run python manage.py migrate
  ```
  What it does:
  - Reads migration files (including Django’s built-in apps).
  - Executes SQL to create/alter tables in `db.sqlite3`.

Useful note:
- If you change a model, you usually run **makemigrations** then **migrate**.

## 8) Inspecting SQLite data (CLI)

Goal: View tables and data directly in SQLite.

1) Open the database file from the project root:
```powershell
sqlite3 db.sqlite3
```

If you're already in sqlite, open the file explicitly (use forward slashes on Windows):
```sql
.open "C:/Users/yubik/Documents/projects/django-sub-tracker/db.sqlite3"
```

2) See which DB file is open:
```sql
.databases
```

3) List tables:
```sql
.tables
```

4) Describe a table (SQLite doesn't have DESCRIBE):
```sql
PRAGMA table_info(subscriptions_expense);
```

5) Run a quick query:
```sql
SELECT * FROM subscriptions_expense;
```

## 9) Renewal processing (transactional)

Goal: Generate subscription expenses safely using a database transaction.

We added a management command:
```powershell
uv run python manage.py renew_subscriptions
```

What it does:
- Finds active subscriptions that are due (`next_renewal_date <= today`)
- In a `transaction.atomic()` block:
  - Creates a subscription expense for **today** (if it doesn't already exist)
  - Advances `next_renewal_date` from **today** by the billing interval

Why transaction matters:
- Expense creation and renewal update succeed together or fail together.

Note:
- We decided to keep renewals manual for now and removed the `autopay_enabled` field.

## 10) Basic JSON API (no DRF)

Endpoints:
- `/api/expenses/` returns a JSON list of expenses
- `/api/monthly-spend/` returns current month total spend

Run the server:
```powershell
uv run python manage.py runserver
```

Test in browser:
```
http://127.0.0.1:8000/api/expenses/
http://127.0.0.1:8000/api/monthly-spend/
```

## 11) Admin action: Renew Now

We added an admin action on Subscriptions:
- Select subscriptions in admin list
- Choose "Renew selected subscriptions now"
- This creates today's expense and advances `next_renewal_date`

## 12) DRF (plan)

We will add Django REST Framework next:
- Install `djangorestframework`
- Add it to `INSTALLED_APPS`
- Create serializers
- Create viewsets + routes
- Test endpoints in browser

## 13) DRF (implemented)

We added:
- `subscriptions/serializers.py`
- `subscriptions/api.py` (ModelViewSets)
- DRF router in `subscriptions/urls.py`

Try these endpoints:
```
http://127.0.0.1:8000/api/categories/
http://127.0.0.1:8000/api/subscriptions/
http://127.0.0.1:8000/api/expenses/
```

To edit data in admin:
```powershell
uv run python manage.py runserver
```
Then open:
```
http://127.0.0.1:8000/admin
```

### Model overview (simple explanation)

We have three main tables (models) and they are connected like this:

- One **User** can have many **Categories**, **Subscriptions**, and **Expenses**.
- One **Category** can have many **Subscriptions** and many **Expenses**.
- One **Subscription** can generate many **Expenses** (renewals).

Think of it as:
User → Category → Subscription → Expense
(Expenses can also be manual and belong directly to a Category.)

### Minimal ER-style diagram

```text
User (auth_user)
  1 ──< Category
  1 ──< Subscription
  1 ──< Expense

Category
  1 ──< Subscription
  1 ──< Expense

Subscription
  1 ──< Expense

Legend: 1 ──< means "one-to-many"
```

#### 1) Category
Purpose: A label to group subscriptions/expenses (e.g., "Streaming", "Utilities").

Fields:
- `user` (required): owner of this category.
- `name`: category name (required).
- `created_at`: auto timestamp.
- `updated_at`: auto timestamp on change.

Rules:
- Category name must be unique per user.

#### 2) Subscription
Purpose: A recurring payment (e.g., Netflix monthly).

Fields:
- `user` (required): owner of this subscription.
- `name`: subscription name.
- `category`: link to Category (required).
- `billing_cycle`: monthly/yearly/custom.
- `billing_interval_months`: used when billing_cycle is custom (auto-set for monthly/yearly).
- `amount`: cost per cycle (non-negative).
- `currency`: 3-letter code like USD.
- `billing_date`: anchor date for billing calculations.
- `next_renewal_date`: next time it should renew (auto-filled if blank).
- `status`: active/paused/cancelled.
- `notes`: optional free text.
- `created_at`, `updated_at`: timestamps.

Rules:
- Amount can’t be negative.
- Interval must be at least 1 month.
- Monthly auto-sets interval to 1, yearly auto-sets to 12.

#### Admin list views
We added `updated_at` to the list display for Category, Subscription, and Expense so you can see recent edits at a glance.

## 7) Model changes and migrations (note on defaults)

If you add a new **required** field to an existing table, Django will ask for a one-off default when you run `makemigrations`. This is so existing rows can be populated.

Example prompt:
- “It is impossible to add a non-nullable field … without specifying a default.”
- Option 1 lets you enter a one-off default (e.g., `timezone.now` or `datetime.date(2026, 1, 28)`).

After `makemigrations`, run:
```powershell
uv run python manage.py migrate
```

#### 3) Expense
Purpose: A single transaction (generated from a subscription or added manually).

Fields:
- `user` (required): owner of this expense.
- `subscription` (optional): link to Subscription if auto-generated.
- `name`: short label for the expense (auto-set from subscription when linked).
- `category` (optional): required for manual expenses.
- `amount`: cost (non-negative).
- `currency`: 3-letter code like USD.
- `transaction_date`: when the expense happened.
- `source`: "subscription" or "manual".
- `notes`: optional.
- `created_at`: auto timestamp.
- `updated_at`: auto timestamp on change.

Rules:
- If `subscription` is set, `source` must be "subscription".
- If `source` is "subscription", `subscription` must be set.
- Manual expenses must have a category.
  Auto-fill for subscription expenses:
  - `transaction_date` uses `subscription.next_renewal_date` if missing.
  - `amount`, `currency`, `category` pull from the subscription if missing.
  - `source` is forced to "subscription".

#### Admin UX note (subscription expenses)
When a subscription is selected in admin, the form disables `source`, `category`,
`amount`, `currency`, and `transaction_date`. They are auto-filled on save.

## Next up

- Create admin user
- Define core models: Category, Subscription, Expense
- Register models in Django admin
