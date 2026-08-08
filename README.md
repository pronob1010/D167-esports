# D167 - Esports / Tournament Site

A Django web application for running game tournaments (currently turf football
focused), with teams, players, matches, rounds, groups, and rankings.

> **Roadmap:** This project is being evolved from a single-tenant demo into a
> rentable, multi-tenant tournament platform. See
> [`PLATFORM_ROADMAP.md`](PLATFORM_ROADMAP.md) for the plan.
>
> **Multi-tenant platform (Stage A + core of Stage B) is now built.** Any user
> can sign up as an **organizer**, get their own dashboard, and create/manage
> their own tournaments in isolation from other organizers.

## Organizer platform

Organizers self-serve through a dedicated, login-protected area (separate from
the public esports site):

| URL | Purpose |
|-----|---------|
| `/organizer/signup/` | Register as an organizer (creates user + organizer profile) |
| `/organizer/dashboard/` | List and manage *your* tournaments only |
| `/organizer/tournaments/new/` | Create a tournament (draft) |
| `/organizer/tournaments/<slug>/` | View / change status / manage a tournament |
| `/organizer/o/<slug>/` | Public read-only page for an organizer |

Key models live in the `organizers` app: **`Organizer`** (the tenant),
**`Game`** (so new games are data, not code), and **`TournamentPayment`**
(records the per-tournament fee; the payment gateway is intentionally not wired
up yet). `Tournament` now carries an `organizer` owner plus `game`, `status`,
`format`, `entry_fee`, `max_teams`, and dates.

Data isolation is enforced in every organizer view and covered by tests in
`organizers/tests.py` (run `python manage.py test organizers`).

## Tech stack

- **Python** 3.8+ (developed on 3.8; 3.11 works)
- **Django** 3.2 (LTS)
- Django admin theming via **jazzmin**, chained selects via **smart_selects**,
  forms via **crispy-forms**

## Project layout

```
D167-esports/
├── requirements.txt
├── PLATFORM_ROADMAP.md
└── esports/                # Django project root (manage.py lives here)
    ├── manage.py
    ├── .env.example        # copy to .env for local config
    ├── esports/            # settings, urls, wsgi/asgi
    ├── Accounts/           # custom User model + auth
    ├── administration/     # site content / sub-admins / sponsors
    ├── teams/              # teams, team players, lineups
    ├── players/            # player profiles
    ├── matches/            # Tournament -> Round -> Group -> Match -> rankings
    ├── templates/          # HTML templates
    ├── static/             # CSS / JS / images
    └── media/              # user uploads (not tracked in git)
```

## Local setup

All commands below are run from the **`esports/`** directory (where `manage.py` is).

1. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r ../requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`. At minimum for real deployments, set a unique
   `DJANGO_SECRET_KEY`. You can generate one with:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   | Variable | Default | Notes |
   |----------|---------|-------|
   | `DJANGO_SECRET_KEY` | insecure dev key | **Must** be set to a random value in production |
   | `DJANGO_DEBUG` | `True` | Set to `False` in production |
   | `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hostnames |

4. **Apply database migrations**

   ```bash
   python manage.py migrate
   ```

   > If Django reports model changes on first run (e.g. after recent bug fixes),
   > run `python manage.py makemigrations` then `migrate` again.

5. **Create an admin user**

   ```bash
   python manage.py createsuperuser
   ```

   (The custom user model logs in with **phone number** as the username field.)

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   - Site: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Notes

- The database is SQLite by default (`db.sqlite3`), which is **not** committed.
  Migration to PostgreSQL is planned (see roadmap Stage A).
- `db.sqlite3`, `media/`, `.env`, and `__pycache__/` are intentionally
  git-ignored.
