# Insurance Agency App — Environment, Requirements & Setup Process

## 1. Environment Overview

Two distinct environments, kept deliberately separate:

| | Development | Production |
|---|---|---|
| Location | Normal git repo, wherever you're coding | Dedicated path on the Linux host (e.g. `/opt/insurance-app/`) |
| Code | Live, actively edited | A copied/synced snapshot from the repo — not a live git checkout being edited in place |
| Database | Local Postgres, dev credentials | Local Postgres, separate production credentials |
| Settings | Dev `.env` (relaxed, `DEBUG=True`) | Prod `.env` (locked down, `DEBUG=False`) — created directly on the server, never committed to git |
| Server process | `manage.py runserver` | gunicorn, supervised by systemd |
| Access | Developer's machine only | Localhost-only on the production machine — no domain, no nginx needed |
| "Always on"? | No — manually started while working | Yes — systemd restarts on crash/reboot |

A setup/deploy script bridges the two: it takes what's in the dev repo and
provisions/updates the production environment. It is not something run
during day-to-day development.

## 2. Requirements

**System-level:**
- Linux (production target; dev machine is Fedora, should generalize fine)
- Python 3.10+ (dev machine currently on 3.14 — Django 6.0 supports it)
- PostgreSQL server, running natively (not containerized) on both dev and prod machines

**Python packages (tracked in `requirements.txt`, grown as the project grows):**
- `django`
- `psycopg2-binary` — Postgres driver
- `django-environ` — reads settings from `.env` instead of hardcoding
- (later) whatever's needed for the Supabase backup call (likely the `supabase` Python client, or plain `requests`/`httpx` if calling its REST API directly)
- (later, only if async backup is chosen) a task queue package, e.g. Celery or Django-Q — see open decision below

**External accounts/services:**
- A Supabase project (separate dev/test project vs. production project — don't point dev at the real backup target)

## 3. Development Setup Process

1. **Create project folder + git repo** — this is the dev root; the setup
   script will later copy from here, not edit it directly.
2. **Create and activate a Python virtual environment** — isolates this
   project's dependencies from the rest of the system.
3. **Install Django + core dependencies**, then freeze to
   `requirements.txt` immediately (and every time a new package is added —
   this file is what the deploy script uses to rebuild the environment on
   the server).
4. **Start the Django project** (`django-admin startproject`) — a
   project-level package (global settings) distinct from the individual
   "apps" (customers, policies, etc.) that will live inside it.
5. **Create the first app(s)** and register them in settings.
6. **Set up environment-variable-driven settings from the start** — `DEBUG`,
   `SECRET_KEY`, database credentials, and (later) Supabase keys all read
   from a `.env` file via `django-environ`, never hardcoded. This is what
   lets the same codebase behave correctly in both dev and prod without
   code changes — only the `.env` differs.
7. **`.gitignore`** — exclude the virtual environment folder, `.env`,
   Python cache files, and any local SQLite/db artifacts.
8. **Create the local dev Postgres role + database**, matching whatever's
   in `.env`. The role should not be a superuser — least privilege, even
   in dev.
9. **Run initial migrations, create a superuser, and run the dev server** —
   confirms Django, Postgres, and settings are all correctly wired together
   before any app-specific code is written.

## 4. Production Setup — What the Deploy Script Should Do

Written once the app itself is built and has been run manually in a
production-like way at least once (venv, gunicorn, `DEBUG=False`) so
whatever breaks has already been seen firsthand.

1. **System prep** — verify/install Python, PostgreSQL server, and any
   build tools needed for Python packages to compile.
2. **Database provisioning** — create the production Postgres role and
   database if they don't already exist (safe to re-run / idempotent).
3. **Sync application files** — copy the app code from the dev repo
   checkout into the production path, excluding dev-only files (`.git`,
   dev `.env`, local test data).
4. **Virtualenv + dependencies** — create the production virtualenv if
   missing, install/update from `requirements.txt`.
5. **Secrets check** — verify a production `.env` exists at the expected
   path; stop and warn rather than silently running with missing secrets.
6. **Django management steps** — run migrations, `collectstatic`, and a
   deploy-oriented system check, so a bad deploy fails loudly instead of
   quietly.
7. **Install/refresh the systemd unit file** — defines how to start the
   app (gunicorn, bound to localhost), restarts it automatically on
   crash, and starts it on boot. This is what makes it "always on."
8. **Reload systemd and restart the service**, then verify it's actually
   active rather than assuming success.
9. **Post-deploy verification** — confirm the app responds on its local
   port before declaring the deploy complete.

**Updates later** follow the same script (or a lighter "update" variant of
it): sync new files → install any new dependencies → run migrations if
models changed → restart the systemd service. Migrations are code (tracked
in git) but must be explicitly *applied* on every environment with a
database — copying files alone does not run them.

## 5. Supabase Backup — Design Notes

- Triggered by Django signals (`post_save`, `post_delete`) on the relevant
  models — fires on every create/update/delete, not on a schedule.
- **Open decision:** synchronous (request waits for the backup call to
  finish — simpler, but a slow/down Supabase connection makes the UI hang)
  vs. asynchronous (queued in the background — needs a task queue running
  as its own supervised process, but staff never notice Supabase issues).
- Supabase credentials live only in the production `.env`, scoped to a
  service role/key with minimal permissions — not a full admin key.
- **Open decision:** what happens when a backup call fails — retry, log
  and move on, or silently skip. Worth deciding deliberately rather than
  discovering a data gap later.

## 6. Open Decisions

- [ ] Sync vs async Supabase backup calls
- [ ] Backup failure handling (retry/log/skip)
- [ ] Exact production path conventions (`/opt/` vs `/srv/`, service
      username, systemd unit naming)
