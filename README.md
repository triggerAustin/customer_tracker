# customer_tracker

An internal Django app for a Kenyan insurance agency to track customers, policies, payments, premium schedules, beneficiaries and claims. It is designed for a single office and a single machine, with staff-only access and no public-facing component.

## Features

- Customer records with phone, email, address, national ID number (unique), KRA PIN and notes.
- Policies linked to a customer, a policy type and an insurer, with coverage and premium amounts, premium frequency, start and expiry dates, and a manually set status (active, lapsed, cancelled, expired).
- Open-ended policy types: staff can add a new type inline from the policy form or the policy list using an HTMX quick-add, without leaving the page.
- Payments per policy (cash, M-Pesa, bank transfer, cheque) with reference number and period covered.
- Premium schedules with pending, paid and overdue states.
- Beneficiaries per policy with percentage share.
- Claims with a full status history (filed, under review, approved, rejected, paid).
- Documents (ID copies, policy documents, claim evidence) attached to exactly one customer, policy or claim.
- Django admin registered for every model.
- A `seed_demo_data` management command that fills the database with realistic Kenyan mock data.

## Tech stack

- Python and Django 6.1
- PostgreSQL (via `psycopg2-binary`)
- `django-environ` for configuration
- HTMX (loaded from unpkg) for inline interactions
- Server-rendered Django templates and plain CSS

## Project layout

```
customer_tracker/
├── config/          # settings, urls, wsgi/asgi
├── customers/       # Customer model, views, forms, templates
├── policies/        # PolicyType, Insurer, Policy, Payment, PremiumSchedule,
│                    # Beneficiary, views, templates, seed_demo_data command
├── claims/          # Claim and ClaimStatusHistory models
├── documents/       # Document model (generic attachment)
├── templates/       # base.html
├── static/css/      # main.css
├── docs/            # dev plan, model notes, environment setup, postmortem
├── manage.py
└── requirements.txt
```

## Data model

```
PolicyType ─┐
Insurer ────┼─> Policy ─┬─> Payment
Customer ───┘           ├─> PremiumSchedule
                        ├─> Beneficiary
                        └─> Claim ──> ClaimStatusHistory

Document ──> exactly one of: Customer, Policy, Claim
```

## Getting started

### Requirements

- Python 3.12 or newer (developed on 3.14)
- PostgreSQL

### Setup

```bash
git clone https://github.com/triggerAustin/customer_tracker.git
cd customer_tracker

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a PostgreSQL database and user, then add a `.env` file in the project root (it is git-ignored):

```
SECRET_KEY=change-me
DEBUG=True
DB_NAME=customer_tracker
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

Apply migrations and create an admin user:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Optionally load demo data (add `--flush` to clear existing records first):

```bash
python manage.py seed_demo_data
```

Run the development server:

```bash
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`, which redirects to the customer list. The admin is at `/admin/`.

## URLs

| Path | Purpose |
| --- | --- |
| `/customers/` | List, create (`new/`), view (`<id>/`) and edit (`<id>/edit/`) customers |
| `/policies/` | List, create, view and edit policies |
| `/policies/policy-types/quick-add/` | HTMX endpoint for adding a policy type inline |
| `/admin/` | Admin for all models, including claims and documents |

## Current status

Done:

- Models and migrations for customers, policies, payments, premium schedules, beneficiaries, claims and documents
- Admin registration for every model
- Customer and policy screens (list, detail, create, edit)
- Demo data seeding

Not yet built:

- Screens for claims and documents (they are managed through the admin for now)
- Login protection on the custom views
- Automated tests (the test files are currently empty)
- Supabase backup triggered by Django signals on every save
- Production setup: gunicorn, systemd service and a deploy script
- Dashboards such as policies expiring soon

## Documentation

Design notes live in `docs/`:

- `docs/insurance-app-dev-plan.md`: overview, environment decisions, build order and decision log
- `docs/files/insurance-app-models.md` and `docs/files/insurance-app-environment-setup.md`: model and environment notes
- `docs/postmortem/postmortem-postgres-connection-issue.md`: write-up of a Postgres connection problem and its fixes

## License

No license has been specified yet.
