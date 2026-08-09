# D167 - Esports / Tournament Site

A Django web application for running game tournaments (currently turf football
focused), with teams, players, matches, rounds, groups, and rankings.

> **Roadmap:** This project is being evolved from a single-tenant demo into a
> rentable, multi-tenant tournament platform. See
> [`PLATFORM_ROADMAP.md`](PLATFORM_ROADMAP.md) for the plan.
>
> **Stages A–E are built.** Any user can sign up as an **organizer**, run
> tournaments end to end (teams, fixtures, scores, standings, knockout
> brackets), collect **public team registrations**, and pay the
> **per-tournament fee via bKash** — all with each organizer isolated from
> the others. The platform is **multi-game**: **Turf Football** and **Cricket**
> ship seeded, and each game carries its own scoring rules.

## Organizer platform

Organizers self-serve through a dedicated, login-protected area (separate from
the public esports site):

| URL | Purpose |
|-----|---------|
| `/organizer/signup/` | Register as an organizer (creates user + organizer profile) |
| `/organizer/dashboard/` | List and manage *your* tournaments only |
| `/organizer/tournaments/new/` | Create a tournament (draft) |
| `/organizer/tournaments/<slug>/` | View / change status / manage a tournament |
| `/organizer/tournaments/<slug>/teams/` | Add teams, generate fixtures |
| `/organizer/tournaments/<slug>/fixtures/` | Enter scores (league & knockout) |
| `/organizer/tournaments/<slug>/standings/` | Live league table |
| `/organizer/tournaments/<slug>/registrations/` | Review & approve/reject team sign-ups |
| `/organizer/billing/` | Per-tournament fees and their status |

### Public pages (no login)

| URL | Purpose |
|-----|---------|
| `/organizer/o/<slug>/` | An organizer's public page (their tournaments) |
| `/organizer/t/<slug>/` | Public tournament page (fixtures, standings) |
| `/organizer/t/<slug>/register/` | Team captains register their team |

Key models: **`Organizer`** (the tenant), **`Game`** (so new games are data, not
code), **`TournamentPayment`** (per-tournament fee + bKash tracking),
**`TournamentTeam`** (a tournament's participants), and
**`TournamentRegistration`** (public sign-ups awaiting approval). `Tournament`
carries an `organizer` owner plus `game`, `status`, `format`, `entry_fee`,
`max_teams`, and dates. Fixture/standings logic lives in `matches/services.py`.

**Multi-game:** each `Game` row carries its own scoring rules — `points_win`,
`points_draw`, `points_loss`, `score_noun` ("goals"/"runs"), and `draw_label`
("Draw"/"Tie") — so standings are computed per game (football 3/1/0, cricket
2/1/0). **Turf Football** and **Cricket** are seeded via migrations; adding
another game (e.g. Valorant) is a new `Game` row, no code change. Fixture
generation, brackets, score entry, registration, and payments are all
game-agnostic.

**Notifications:** registration emails use Django's email backend, which
defaults to the **console** backend (prints to the server log) in development.
Set `DJANGO_EMAIL_BACKEND` and the SMTP vars for real delivery. SMS can be added
later behind `organizers/notifications.py`.

**Payments (bKash):** the per-tournament fee is paid via **bKash Tokenized
Checkout**. An organizer must settle the fee before a tournament can open
registration. The gateway layer lives in `organizers/payments/`:

- If bKash is not configured, a **dummy gateway** is used so the pay flow works
  end to end in development (no real charge).
- To enable real bKash, set `BKASH_ENABLED=True` and the credentials:
  `BKASH_BASE_URL` (defaults to the sandbox), `BKASH_APP_KEY`,
  `BKASH_APP_SECRET`, `BKASH_USERNAME`, `BKASH_PASSWORD`.
- The fee amount comes from `TOURNAMENT_FEE` (default 500 BDT); a zero fee is
  auto-waived. Organizers see their charges at `/organizer/billing/`.

Data isolation is enforced in every organizer view and covered by tests
(`python manage.py test` — organizers + matches).

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
    ├── organizers/         # tenant layer: Organizer, Game, registrations, payments
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
   | `TOURNAMENT_FEE` | `500` | Per-tournament fee in BDT (0 = free) |
   | `BKASH_ENABLED` | `False` | `True` + credentials to use real bKash |

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
