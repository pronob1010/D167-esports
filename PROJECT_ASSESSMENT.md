# D167 E-Sports — Project Assessment & Roadmap

_Assessment date: 2026-06-13_

This document reviews the current state of the **D167 E-Sports** Django project
and lays out a concrete plan for "giving it shape" — turning the working
prototype into a maintainable, production-ready application.

---

## 1. What this project is

A **Django web application for an e-sports organization** (battle-royale /
PUBG-style point-table tournaments). It is a server-rendered site built on a
purchased "soccer/esports" HTML theme wired into Django templates.

**Stack**
- Django 3.2.5, Python (was developed on 3.8, container has 3.11)
- SQLite database
- Server-rendered Django templates (no JS framework, no REST API)
- Third-party apps: `jazzmin` (admin skin), `smart_selects` (chained dropdowns),
  `crispy_forms`

**Apps & domain model**

| App | Responsibility | Key models |
|-----|----------------|------------|
| `Accounts` | Custom user (login by **phone**), profile, social links | `User`, `UserProfile`, `UserSocialMedia` |
| `teams` | Teams, rosters, "central" team per game, achievements | `Team`, `TeamPlayers`, `CentralTeam`, `OtherLineUp`, `CentralTeamAchievement` |
| `players` | Player profiles (auto-created from users) | `Player` |
| `matches` | Tournament hierarchy + scoring | `Tournament` → `MatchRound` → `MatchGroup` → `Match` → `RegisteredTeams` / `PlayersPointTable` |
| `administration` | Site config, sponsors, broadcasts, sub-admins, public pages | `SiteInfo`, `SiteAbout`, `sponsor_details`, `broadcast`, `SubAdmin`, `LegendZone` |

**Core feature that works:** computing and displaying point tables (kills +
placement points) at tournament / round / group level, plus an MVP/ranking
list and per-player stats. Content is managed entirely through the Django
admin.

**Overall verdict:** A functional MVP with a real, non-trivial feature set. The
*ideas* and data model are sound. What's missing is the engineering hygiene
that makes it reproducible, safe, fast, and maintainable.

---

## 2. Critical issues (fix first — these block reliable use)

### 2.1 No dependency management
There is **no `requirements.txt`, `Pipfile`, or `pyproject.toml`**. Django
isn't even installed in a fresh checkout, so the project cannot be reproduced or
deployed. This is the single biggest blocker.

> **Fix:** Pin dependencies — `django==3.2.x`, `django-jazzmin`,
> `django-smart-selects`, `django-crispy-forms`, `Pillow` — in a
> `requirements.txt` (or better, `pyproject.toml`).

### 2.2 Secrets and debug settings committed
- `SECRET_KEY` is hardcoded in `settings.py` and committed to git.
- `DEBUG = True` is committed.
- `ALLOWED_HOSTS = []` — nothing configured for any real host.

> **Fix:** Move `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and DB credentials to
> environment variables (e.g. `django-environ` / `python-dotenv`). Rotate the
> exposed key.

### 2.3 Generated artifacts committed to git
The repo tracks files that should never be in version control:
- `db.sqlite3` (the actual database, 428 KB)
- **149 `.pyc` files** and `__pycache__/` directories
- **103 uploaded media files** under `media/`

There is **no `.gitignore`**.

> **Fix:** Add a Python/Django `.gitignore`, then
> `git rm --cached` the database, `.pyc` files, `__pycache__`, and `media/`.

### 2.4 Template directory misconfiguration (latent bug)
```python
'DIRS': [ os.path.join('BASE_DIR','../templates') ]
```
This joins the **literal string** `"BASE_DIR"` (not the variable) with
`../templates`, producing a relative path that only resolves by accident
depending on the working directory.

> **Fix:** `'DIRS': [ BASE_DIR / 'templates' ]`.

---

## 3. Correctness bugs

- **`teams/models.py`** — several `null=Team` instead of `null=True`
  (`CentralTeam.BS_team`, `OtherLineUp.team`). `Team` is a truthy class, so it
  "works" by accident but is wrong and confusing.
- **`Accounts/views.py`** imports `from django.contrib.auth.models import User`
  but the project uses a **custom user model** (`AUTH_USER_MODEL =
  'Accounts.User'`). The import is unused here but is a footgun.
- **Login vs. `USERNAME_FIELD`** — `USERNAME_FIELD = 'phone'`, yet the login
  view uses Django's default `AuthenticationForm` (labelled "username") and the
  signup form collects `username` + `phone` only. Worth an end-to-end test to
  confirm login actually works as intended.
- **`rankList` / queries using `and`** — filters like
  `filter(Q(...) and Q(...) and Q(...))` use Python's `and`, which returns only
  the **last** `Q` object. The intended filtering is silently not applied. Use
  `,` or `&` between Q objects.
- **Password validation effectively disabled** — every validator is commented
  out except `NumericPasswordValidator`, so weak passwords are accepted.

---

## 4. Performance

The `matches/views.py::data_table` view is the main concern. It builds the
point table with **deeply nested Python loops (up to triple-nested) that run
fresh ORM queries inside each loop iteration** (classic N+1, here closer to
N³). On a small dataset it's fine; with real tournament data it will be slow.

> **Fix:** Replace the manual aggregation with ORM `annotate()` /
> `aggregate()` (`Sum`, `Count`, `Case/When`) and `select_related` /
> `prefetch_related`. This collapses dozens of queries into a handful and
> removes most of the loop logic.

Other items: no pagination, no caching, no DB indexes on slug/foreign-key
lookup fields.

---

## 5. Code quality & maintainability

- **No tests.** All five `tests.py` files are empty stubs. There is no CI.
- **Dead code everywhere** — large commented-out blocks in models and views
  (`Tournament`, `PlayersPointTable`, chained fields, signals, debug `print`s).
- **`print()` debugging** left in production views.
- **Naming conventions** — model fields use PascalCase / mixed case
  (`TeamName`, `Match_Title`, `Round_title`). Non-idiomatic; should be
  `snake_case`. (Renaming is a breaking change — do it deliberately with
  migrations, or defer.)
- **Business logic lives in views.** The scoring logic belongs on model
  managers / a `services.py` layer so it's testable and reusable.
- **No documentation** — no `README`, setup steps, or architecture notes.
- **`TIME_ZONE = 'Asia/Dhaka'`** with `USE_TZ = True` — fine, just confirm it's
  intentional.

---

## 6. Production-readiness gaps

- SQLite is unsuitable for concurrent production load → move to PostgreSQL.
- No static-file strategy for production (`collectstatic`, WhiteNoise/CDN);
  `STATIC_ROOT` is not set.
- No WSGI/ASGI server config (gunicorn/uvicorn), no reverse-proxy notes.
- No security middleware hardening (`SECURE_*`, HSTS, secure cookies, etc.).
- No error monitoring / logging configuration.
- No deployment artifacts (Dockerfile, Procfile, CI/CD).

---

## 7. Recommended roadmap

A phased plan, ordered so each phase delivers a safer, more workable codebase.

### Phase 0 — Make it reproducible (½–1 day)
1. Add `requirements.txt` (pinned) and a `README.md` with setup steps.
2. Add `.gitignore`; untrack `db.sqlite3`, `*.pyc`, `__pycache__/`, `media/`.
3. Fix the `TEMPLATES['DIRS']` bug so it works regardless of CWD.
4. Verify `python manage.py runserver` + admin login from a clean clone.

### Phase 1 — Secure the basics (½–1 day)
1. Move `SECRET_KEY` / `DEBUG` / `ALLOWED_HOSTS` / DB config to env vars; rotate
   the committed secret key.
2. Re-enable Django's password validators.
3. Split settings into `base` / `dev` / `prod` (or env-driven toggles).

### Phase 2 — Correctness & tests (2–3 days)
1. Fix the `Q(...) and Q(...)` filter bugs and the `null=Team` typos.
2. Confirm signup/login works end to end with the phone-based user model.
3. Add tests: model save/slug logic, point-table aggregation, auth flow,
   smoke tests for every view. Wire up GitHub Actions CI.
4. Remove dead code and `print()` statements.

### Phase 3 — Performance refactor (2–4 days)
1. Rewrite `data_table` (and `rankList`) using ORM aggregation +
   `select_related`/`prefetch_related`.
2. Move scoring logic into model managers / a `services` layer.
3. Add pagination and DB indexes; add caching where it pays off.

### Phase 4 — Production hardening (2–3 days)
1. PostgreSQL, `collectstatic` + WhiteNoise, gunicorn.
2. Security settings (HSTS, secure cookies, `SECURE_SSL_REDIRECT`, etc.).
3. Dockerfile + deployment pipeline; logging + error monitoring.

### Phase 5 — Product polish (ongoing, optional)
- Replace the placeholder `<title>Team HTML</title>` and theme leftovers.
- Decide on naming-convention cleanup (snake_case) as a deliberate migration.
- Consider a DRF API + JS frontend if you want live/dynamic match updates.
- Image optimization for the heavy media library.

---

## 8. Quick wins (can do today)

- [ ] `requirements.txt`
- [ ] `.gitignore` + untrack `db.sqlite3` / `.pyc` / `media`
- [ ] Fix `TEMPLATES['DIRS']`
- [ ] Move `SECRET_KEY` / `DEBUG` to env vars
- [ ] `README.md` with run instructions
- [ ] Delete `print()` debug statements
- [ ] Fix `null=Team` → `null=True`

---

### Bottom line
The product logic is real and the data model is reasonable — this is a salvageable,
genuinely useful MVP. The work to "give it shape" is **engineering discipline**:
make it reproducible, lock down secrets, stop committing artifacts, add tests, and
refactor the point-table query. Phases 0–2 alone would move it from "works on the
author's machine" to "a maintainable project anyone can run and trust."
