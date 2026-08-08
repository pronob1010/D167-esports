# D167 - Esports / Tournament Site

A Django web application for running game tournaments (currently turf football
focused), with teams, players, matches, rounds, groups, and rankings.

> **Roadmap:** This project is being evolved from a single-tenant demo into a
> rentable, multi-tenant tournament platform. See
> [`PLATFORM_ROADMAP.md`](PLATFORM_ROADMAP.md) for the plan.

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
