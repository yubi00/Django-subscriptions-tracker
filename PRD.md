# Subscription & Expense Tracker

## Product Requirements Document (PRD)

---

## 1. Overview

**Subscription & Expense Tracker** is a Django-based web application that helps users track recurring subscriptions and one-off expenses, understand their monthly and yearly spending, and receive alerts before renewals.

The project is intentionally designed as a **realistic, production-style backend system**, focusing on data integrity, automation, and reporting rather than UI complexity.

This document serves as the **single source of truth** for product scope, assumptions, and implementation direction.

---

## 2. Goals & Non-Goals

### Goals
- Track recurring subscriptions and one-off expenses
- Automatically generate expense records on subscription renewals
- Provide clear monthly and yearly spending insights
- Enforce strong data integrity at the database level
- Demonstrate clean Django architecture and best practices

### Non-Goals (Initial Phase)
- Multi-currency conversion using live FX rates
- Payment processing (Stripe, PayPal, etc.)
- Mobile-native application
- Social or shared accounts

---

## 3. Target Users

- Individuals tracking personal finances
- Developers learning Django through a realistic backend project
- Future potential: small households or freelancers

---

## 4. Core Concepts & Terminology

| Term | Description |
|-----|-------------|
| Subscription | A recurring payment (monthly, yearly, or custom interval) |
| Expense | A single financial transaction (auto-generated or manual) |
| Renewal | The moment a subscription generates a new expense |
| Category | Logical grouping for subscriptions and expenses |

---

## 5. Functional Requirements

### 5.1 Authentication & User Management

- User registration and login
- Password reset via email
- User profile settings:
  - Preferred currency
  - Timezone
  - Optional monthly budget

---

### 5.2 Subscription Management

Each subscription must support:

- Service name
- Category
- Billing cycle:
  - Monthly
  - Yearly
  - Custom (every N months)
- Amount (non-negative)
- Currency
- Start date
- Next renewal date (derived)
- Status:
  - Active
  - Paused
  - Cancelled
- Optional notes

#### Actions
- Create subscription
- Edit subscription
- Pause subscription
- Cancel subscription (soft delete)
- Clone subscription

---

### 5.3 Expense Management

#### Automatic Expenses
- Generated automatically on each renewal
- Immutable once created
- Linked to a subscription

#### Manual Expenses
- One-off expenses
- Categorized
- User-defined date and amount

#### Expense Fields
- Amount
- Category
- Date
- Source (subscription or manual)
- Notes (optional)

---

### 5.4 Dashboards & Reporting

#### Monthly Dashboard
- Total spend
- Subscription spend vs manual spend
- Top subscriptions by cost

#### Yearly Insights
- Projected yearly spend
- Monthly average

#### Category Breakdown
- Aggregated totals per category

All dashboards should be backed by **efficient database queries**, not Python loops.

---

### 5.5 Renewal Alerts & Notifications

- Email reminders before renewals (configurable days)
- Optional weekly summary email
- Background processing via task queue

---

### 5.6 Exporting & Reporting

- Export expenses as CSV
- Filters:
  - Date range
  - Category
  - Subscription-only vs all expenses

---

### 5.7 Admin & Internal Tooling

- Django Admin enabled
- Admin search:
  - Users
  - Subscriptions
- Read-only expense audit view

---

## 6. Non-Functional Requirements

### Performance
- Pagination on all list endpoints
- Indexes on frequently queried fields
- Avoid N+1 queries

### Data Integrity
- Database-level constraints
- Transactions for renewal processing
- Idempotent background jobs

### Security
- CSRF protection
- Secure password storage
- User-level data isolation

---

## 7. Assumptions

- Single-user accounts (no shared access)
- All amounts stored as decimals
- No automatic currency conversion
- Subscription renewals are deterministic

---

## 8. Architecture Overview

### Backend
- Django (latest LTS)
- PostgreSQL
- Django ORM
- Django Admin

### Optional Components
- Django REST Framework
- Celery / Django-Q / Huey
- Redis (caching & task broker)

---

## 9. Data Modeling Principles

- Normalize data
- Avoid duplication
- Prefer derived fields over stored values when possible
- Use soft deletes for historical accuracy

---

## 10. MVP Scope

### Included
- Auth & profiles
- Subscriptions CRUD
- Automatic expense generation
- Monthly dashboard
- CSV export

### Excluded (Future)
- Email reminders
- REST API
- Caching
- Charts

---

## 11. Future Enhancements

- REST API for frontend/mobile
- Budget alerts
- Multi-currency support
- Charts & visualizations
- Public demo mode

---

## 12. Success Criteria

- Clean schema with constraints
- Clear, readable business logic
- Efficient queries for dashboards
- Easy local setup
- Interview-ready explanation

---

## 13. Development Principles

- Schema-first development
- Explicit over implicit logic
- Database as the source of truth
- Clear separation of concerns

---

## 14. Getting Started (To Be Completed)

This section will be filled once implementation begins.

---

## 15. License

MIT (or to be decided)

