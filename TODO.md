## Setup
- [x] Confirm Python version (3.12 or 3.13) and uv version
- [x] Create project virtualenv with uv (`uv venv .venv`)
- [x] Install Django 5.2 LTS in the venv
- [x] Verify Django install and version
- [x] Start Django project (`django-admin startproject config .`)
- [x] Create app `subscriptions`
- [x] Run initial migrations
- [x] Create admin user for Django admin

## Subscription Tracker MVP (Admin-only)
- [x] Define core models (Category, Subscription, Expense)
- [x] Add constraints/choices (status, billing cycle, non-negative amounts)
- [x] Add derived fields logic (next_renewal_date)
- [x] Register models in admin
- [x] Admin list display + filters (status, category, renewal date)
- [x] Create and run migrations
- [x] Verify CRUD in Django admin
- [x] Add Expense name field and auto-fill for subscription expenses
- [x] Admin UX: auto-fill + disable fields for subscription expenses
- [x] Renewal processing command (transactional)

## Basic JSON API (no DRF yet)
- [x] Add /api/expenses endpoint
- [x] Add /api/monthly-spend endpoint

## Notes / Decisions
- [ ] Confirm database: SQLite now, PostgreSQL later
- [ ] Confirm no auth for now (admin-only usage)
## Tools / Data inspection
- [x] Inspect SQLite data via CLI

## Later: PostgreSQL migration
- [ ] Install PostgreSQL and create a database/user
- [ ] Install Python driver (`psycopg`)
- [ ] Update `config/settings.py` database settings
- [ ] Run migrations on PostgreSQL
- [ ] (Optional) Migrate existing data from SQLite

## Later: REST API (Django REST Framework)
- [ ] Install `djangorestframework`
- [ ] Add DRF to `INSTALLED_APPS`
- [ ] Create serializers for Category, Subscription, Expense
- [ ] Create viewsets and routes
- [ ] Add basic filtering and pagination

## DRF (Now)
- [x] Install `djangorestframework`
- [x] Add DRF to `INSTALLED_APPS`
- [x] Add serializers
- [x] Add viewsets + routers
- [ ] Test API in browser
- [ ] Add OpenAPI/Swagger docs (drf-spectacular)

## REST API (Next)
- [ ] Authentication & permissions
- [ ] Pagination
- [ ] Filtering & ordering
- [ ] Validation rules in serializers
- [ ] Consistent error responses
- [ ] Throttling / rate limiting
- [ ] API versioning
- [ ] API tests (DRF test client)
- [ ] CORS setup (frontend access)
- [ ] Docs polish (examples, descriptions)
