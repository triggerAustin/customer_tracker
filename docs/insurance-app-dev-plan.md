# Insurance Agency App — Development Plan & Tracker

_Last updated: 2026-08-18_

## 1. Project Overview

Internal-use Django app for a Kenyan insurance agency, tracking customers,
policies, payments, and claims. Single machine, single office, staff-only
access (no public-facing component).

## 2. Environment & Access

| Item | Decision |
|---|---|
| Access model | Localhost only, on the machine it runs on — no domain, no nginx |
| Always-on | systemd service (not Docker) |
| Dev machine | Fedora, Python 3.14 (system Python, used as-is) |
| Primary DB | PostgreSQL, native install |
| Backup DB | Supabase (hosted Postgres) — backup triggered on every save/change via Django signals |
| pgAdmin | Already running in Docker on dev machine (kept as-is) |
| Dev vs Prod | Separate: normal git repo for dev; a setup/deploy script copies files + provisions prod separately (not a live git checkout) |
| Auth | Single shared login for now — no individual staff accounts |

## 3. Data Model (conceptual — not yet built)

```
PolicyType
 └── Policy (many policies can share a type)

Customer
 └── Policy (many per customer)
       ├── Payment (many per policy)
       └── Claim (many per policy)
              └── ClaimStatusHistory (many status entries per claim)
```

### Customer
- Full name
- Phone number
- Email
- Physical/postal address
- National ID number
- KRA PIN
- Date registered/onboarded
- Notes

### PolicyType
_Open-ended — staff can add new types freely, not a fixed list._
- Name (e.g. Motor, Life, Health, Property)
- Description (optional)

### Policy
- Customer (link)
- Policy type (link)
- Policy number (agency/insurer reference)
- Coverage amount
- Premium amount
- Premium frequency (monthly/quarterly/annually)
- Start date
- Expiry/renewal date
- Status — **manually set by staff** (active/lapsed/cancelled/expired)
- Underwriter/insurer name
- Notes

### Payment
- Policy (link)
- Amount paid
- Date paid
- Payment method (cash, M-Pesa, bank transfer, cheque)
- Reference/transaction number
- Period covered (e.g. "Jan–Mar premium")
- Notes

### Claim
- Policy (link)
- Date filed
- Description
- Amount claimed
- Amount approved/paid
- Current status (mirrors latest ClaimStatusHistory entry)
- Notes

### ClaimStatusHistory
_Full history of status changes, not just a single current-status field._
- Claim (link)
- Status (filed / under review / approved / rejected / paid)
- Date of change
- Note (free text — no per-user attribution since login is shared)

## 4. Build Order (recommended)

1. ✅ Django project scaffold + admin working locally (`runserver`, superuser, Postgres connection confirmed)
2. ⬜ Build models above (`customers`, `policies` apps — or however you choose to split them)
3. ⬜ Migrations + confirm in Postgres/pgAdmin that tables look right
4. ⬜ Django admin registration for all models (fastest way to test data entry before building custom views)
5. ⬜ Supabase backup logic (signals on save/delete) — decide sync vs async
6. ⬜ Any custom views/dashboards beyond the built-in admin (e.g. "policies expiring soon" list)
7. ⬜ Environment-variable-driven settings finalized (DEBUG, SECRET_KEY, DB creds, Supabase keys)
8. ⬜ Manually run the app in a production-like way once (venv, gunicorn, `DEBUG=False`) before automating
9. ⬜ Write the setup/deploy script (system prep, DB provisioning, file sync, venv, migrate, collectstatic, systemd unit install/restart)
10. ⬜ Deploy to production machine, verify systemd service survives reboot

## 5. Open Decisions / Questions (fill in as they come up)

- [ ] Exact list of policy statuses to use (active/lapsed/cancelled/expired — confirm final wording)
- [ ] Exact list of claim statuses/stages
- [ ] Sync vs async for Supabase backup calls
- [ ] What happens if a Supabase backup call fails (retry? log? ignore?)
- [ ] Any reporting/dashboard needs beyond raw record lists (e.g. expiring policies, outstanding claims)

## 6. Decision Log

| Date | Decision |
|---|---|
| 2026-08-18 | Chose PostgreSQL (not SQLite) for local primary DB |
| 2026-08-18 | Access is localhost-only; always-on via systemd, no nginx/domain needed |
| 2026-08-18 | Supabase backup triggered on every save/change (signals), not scheduled |
| 2026-08-18 | Staying on Python 3.14 as installed rather than pinning an older version |
| 2026-08-18 | Decided against Docker for Django — native install + systemd; Postgres stays native, pgAdmin stays Dockerized |
| 2026-08-18 | Policy types are open-ended (staff-managed lookup table) |
| 2026-08-18 | Policy status is manually set by staff, not auto-computed |
| 2026-08-18 | Claims require full status history, not a single status field |
| 2026-08-18 | Customer records include National ID and KRA PIN |
| 2026-08-18 | Single shared login for now — no individual staff accounts |
