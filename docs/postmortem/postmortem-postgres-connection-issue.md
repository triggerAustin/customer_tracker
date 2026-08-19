# Postmortem — Django Not Connecting to Postgres

**Date:** 2026-08-18
**Component:** `customer_tracker` Django project — database configuration
**Status:** Resolved

## Summary

After building the initial data models (`customers`, `policies`, `claims`,
`documents`) and running `makemigrations` / `migrate`, no new tables
appeared in pgAdmin. Root cause was a chain of three separate
misconfigurations, each masking the next, rather than a single bug.

## Impact

- Migrations for all four apps ran successfully against the wrong
  database (SQLite) with no error, giving false confidence that the
  database layer was working.
- Time lost diagnosing "missing tables" in pgAdmin before the underlying
  cause (wrong DB engine) was identified.
- No data loss — this was caught before any real records were entered.

## Timeline of Root Causes (in the order they were found and fixed)

### 1. `settings.py` was still using Django's default SQLite config

**Symptom:** `migrate` completed without error, but pgAdmin showed no new
tables.

**Cause:** `django-admin startproject` generates a default `DATABASES`
block pointing at a local `db.sqlite3` file. The project's `.env` file
had all the correct Postgres credentials, but nothing in `settings.py`
was reading them yet — `django-environ` had never been wired in.
Migrations were being applied successfully, just to the wrong database
entirely, with zero indication anything was wrong.

**Fix:** Added `django-environ` initialization to `settings.py` and
replaced the hardcoded SQLite `DATABASES` block with one reading
`ENGINE`, `NAME`, `USER`, `PASSWORD`, `HOST`, and `PORT` from `.env`.

**Lesson:** A framework default that "just works" (SQLite requires no
setup) can silently stand in for the real target and produce no errors.
Verifying which database engine is actually active should be an explicit
early check, not an assumption — especially right after scaffolding a new
project.

---

### 2. `environ.Env()` was instantiated but never told to read the `.env` file

**Symptom:** `KeyError: 'SECRET_KEY'` when running `makemigrations`, even
though `.env` had the correct value.

**Cause:** `env = environ.Env()` only creates the reader object — it does
not automatically load any file. The required follow-up call,
`environ.Env.read_env(BASE_DIR / '.env')`, was missing, so `environ`
only ever checked real OS environment variables (which were empty) and
found nothing.

**Fix:** Added `environ.Env.read_env(BASE_DIR / '.env')` immediately
after `env = environ.Env()`, positioned after `BASE_DIR` is defined and
before any `env(...)` calls elsewhere in the file.

**Lesson:** Two-step initialization patterns (create object, then load
data into it) are an easy step to drop when following a checklist from
memory rather than documentation. Order-of-operations in `settings.py`
matters — anything reading from `env()` must come after both `BASE_DIR`
and `read_env()`.

---

### 3. The target Postgres database didn't exist yet

**Symptom:** `RuntimeWarning` during `makemigrations`:
`FATAL: database "Customer_tracker" does not exist`, followed by
`No changes detected`.

**Cause:** The Postgres *server* was running and reachable on
`localhost:5432`, but the specific database named in `.env`
(`Customer_tracker`) had never been created. A running server does not
imply the named database exists inside it.

**Fix:** Created the database directly (`createdb Customer_tracker`, or
via pgAdmin's Create Database dialog), matching the exact
capitalization used in `.env`.

**Lesson:** "Can I connect to the server" and "does my specific database
exist on that server" are two different failure points and should be
checked separately when diagnosing connection issues.

---

### 4. (Secondary, non-blocking) Stale migration files from the SQLite run

**Symptom:** `No changes detected` on `makemigrations` even after the
Postgres connection was fixed.

**Cause:** Migration files generated during the SQLite phase
(`0001_initial.py` in each app's `migrations/` folder) were already on
disk, so Django considered the models already accounted for and didn't
regenerate anything.

**Fix:** Confirmed old migration files were removed (keeping
`__init__.py`) before re-running `makemigrations` against the corrected
Postgres connection.

**Lesson:** Migration files are tied to a migration *history*, not a
specific database — switching the underlying database engine after
migrations already exist calls for a clean slate on the migration files,
not just a fix to the connection settings.

## What Went Well

- Each failure produced a distinct, legible error message once actually
  triggered — no silent data corruption.
- Following the `.env` → settings.py → migrate chain step by step
  isolated each cause without needing to guess.

## Follow-up / Preventive Notes

- When starting a new Django project that will use Postgres from day
  one, verify the `DATABASES` block and `django-environ` wiring
  **before** writing any models — catch this class of issue before
  migrations exist at all, not after.
- Worth remembering going forward: a successful `migrate` run is not
  itself proof of connecting to the intended database — confirm the
  engine/host/db name being used matches expectations, especially early
  in a project.
