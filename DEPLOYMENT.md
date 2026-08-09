# Production Deployment Checklist — D167 Tournament Platform

This is the practical, project-specific checklist to take D167 from
"works and tested locally" to "real organizers using it." Work top to bottom;
each step says **what to do** and **why**.

> **Legend:** ✅ already handled in the code · ⚙️ needs a settings/config change ·
> ➕ needs something added (dependency, service, or infra).

---

## 0. Pre-flight (quick sanity)

- [ ] `pip install -r requirements.txt` on a clean environment succeeds.
- [ ] `python manage.py check --deploy` reviewed (it warns about the security
      settings covered in step 4).
- [ ] `python manage.py test` is green.
- [ ] You have chosen a host (VPS, Railway, Render, Fly, etc.) and a domain.

---

## 1. Secrets & core config ✅ (already env-driven)

All of these are already read from the environment (see `esports/settings.py`).
Set them as **real environment variables** on the host — do **not** commit them.

| Variable | Production value |
|----------|------------------|
| `DJANGO_SECRET_KEY` | A fresh random string (see below). **Required.** |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `d167.example.com,www.d167.example.com` |
| `TIME_ZONE` | already `Asia/Dhaka` in settings |

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- [ ] `DJANGO_SECRET_KEY` set to a unique value (never the dev default).
- [ ] `DJANGO_DEBUG=False`.
- [ ] `DJANGO_ALLOWED_HOSTS` lists your real domain(s), no spaces.

---

## 2. Database — move to PostgreSQL ⚙️➕

SQLite is fine for the demo but not for production (concurrent writes, backups,
integrity). The code is DB-agnostic, so this is a settings + dependency change.

**a. Add the driver** (`requirements.txt`):

```
psycopg2-binary>=2.9
```

**b. Make `DATABASES` env-driven** — replace the SQLite block in
`esports/settings.py` with:

```python
if os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", ""),
            "USER": os.environ.get("POSTGRES_USER", ""),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {  # local development fallback
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

> Or use `dj-database-url` and a single `DATABASE_URL` if your host provides one
> (Railway/Render/Heroku do).

- [ ] `psycopg2-binary` added and installed.
- [ ] `DATABASES` reads from env; Postgres credentials set on the host.
- [ ] `python manage.py migrate` run against Postgres (creates schema + seeds
      **Turf Football** and **Cricket** via the data migrations).
- [ ] `python manage.py createsuperuser` (logs in with **phone number**, not email).

---

## 3. Static & media files ⚙️➕

The app serves CSS/JS/images (`static/`) and user uploads (`media/`: team logos,
match images, organizer logos). In production Django does **not** serve these —
you need `collectstatic` + a real file server.

**a. Add `STATIC_ROOT`** to `esports/settings.py` (currently missing):

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

**b. Serve static files.** Simplest is **WhiteNoise** (no nginx needed for
static):

```
# requirements.txt
whitenoise>=6.0
```

```python
# settings.py — add right after SecurityMiddleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...the rest unchanged...
]
# Django 3.2 (this project):
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

**c. Media files.** `media/` is **user-uploaded** and must persist and be served.
Currently `esports/urls.py` serves media via Django unconditionally — fine for
dev, not for production. Options:
- **nginx** location block for `/media/` (recommended on a VPS), or
- object storage (S3-compatible) via `django-storages`, or
- for a first small launch, keep Django serving media but put it behind your web
  server and on persistent storage.

- [ ] `STATIC_ROOT` set; `python manage.py collectstatic --noinput` runs clean.
- [ ] Static files load over the deployed site (check the organizer dashboard CSS
      and the public esports theme).
- [ ] `media/` is on **persistent** storage (not an ephemeral container disk) and
      is served. Uploaded team/organizer logos display.

> Note: the public esports theme (`templates/base.html`) needs a `SiteInfo` row
> to show its logo/nav; create one in `/admin/` or the site header will be bare.
> (The organizer dashboard is self-contained and unaffected.)

---

## 4. Security hardening ⚙️

With `DEBUG=False` behind HTTPS, add these to `esports/settings.py` (gate on
`not DEBUG` so local dev is unaffected):

```python
CSRF_TRUSTED_ORIGINS = [
    "https://" + h for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")
]

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # If behind a reverse proxy / load balancer terminating TLS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
```

- [ ] The block above added and `python manage.py check --deploy` shows no
      critical warnings.
- [ ] `CSRF_TRUSTED_ORIGINS` includes your HTTPS domain (needed for all POST
      forms — login, score entry, payments — to work behind HTTPS).
- [ ] `SECURE_PROXY_SSL_HEADER` set **only if** a proxy terminates TLS (most
      PaaS and nginx setups) — otherwise the bKash callback URL may be built as
      `http://` and fail.

---

## 5. Email (registration notifications) ⚙️

Registration emails currently use the **console** backend (they print to the
log). For real delivery, set SMTP env vars (already wired in settings):

- [ ] `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- [ ] `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT`, `DJANGO_EMAIL_HOST_USER`,
      `DJANGO_EMAIL_HOST_PASSWORD`, `DJANGO_EMAIL_USE_TLS` set.
- [ ] `DJANGO_DEFAULT_FROM_EMAIL` set to a real address on your domain.
- [ ] Send a test registration and confirm the organizer receives the email.

> SMS (useful for local team captains) is not built yet; it can be added behind
> `organizers/notifications.py` without touching the views.

---

## 6. bKash go-live 💳

The payment gateway auto-selects **dummy** unless bKash is enabled. To take real
money you need a bKash **merchant account with PGW / Tokenized Checkout**
credentials.

- [ ] Obtain sandbox credentials; set on the host:
      `BKASH_ENABLED=True`, `BKASH_BASE_URL` (sandbox URL),
      `BKASH_APP_KEY`, `BKASH_APP_SECRET`, `BKASH_USERNAME`, `BKASH_PASSWORD`.
- [ ] Run a **sandbox** test payment end to end (create tournament → Pay →
      complete on bKash → returns to callback → status becomes **Paid**,
      transaction ID recorded, registration can open).
- [ ] In the bKash merchant panel, whitelist the callback URL — the app builds
      `https://your-domain/organizer/tournaments/<slug>/pay/callback/`. Ensure
      the site is HTTPS so the callback is built as `https://` (see step 4).
- [ ] Switch `BKASH_BASE_URL` to the **live** endpoint and swap in live
      credentials only after the sandbox test passes.
- [ ] Decide `TOURNAMENT_FEE` (BDT). `0` = free/auto-waived.

> The bKash client is written to the tokenized-checkout spec but can only be
> fully verified against bKash's sandbox with real keys — always do the sandbox
> transaction before going live.

---

## 7. Application server ➕

Do **not** use `manage.py runserver` in production. Use Gunicorn:

```
# requirements.txt
gunicorn>=21.0
```

```bash
# from the esports/ directory
gunicorn esports.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

- [ ] Gunicorn added and serves the app.
- [ ] Process is supervised (systemd unit, or the platform's process manager /
      `Procfile: web: gunicorn esports.wsgi --chdir esports`).
- [ ] `WEB_CONCURRENCY` / `--workers` tuned to the host (2×CPU + 1 is a start).

---

## 8. Web server & TLS ⚙️➕

- [ ] HTTPS enabled with a valid certificate (Let's Encrypt via nginx/Caddy, or
      automatic on a PaaS).
- [ ] On a VPS: nginx reverse-proxies to Gunicorn and serves `/static/` and
      `/media/` directly. On a PaaS: WhiteNoise handles static; use object
      storage or a mounted volume for media.
- [ ] HTTP → HTTPS redirect works (also enforced by `SECURE_SSL_REDIRECT`).

---

## 9. Deploy, run & verify ✅➡️

Run these on the server (from `esports/`), in order:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser        # first deploy only
python manage.py check --deploy
```

Then smoke-test the live site:

- [ ] `/admin/` loads and you can log in (phone number as username).
- [ ] Create a `SiteInfo` row in admin (for the public esports theme).
- [ ] `/organizer/signup/` → create an organizer → dashboard loads with styling.
- [ ] Create a tournament (football **and** cricket), pay the fee (sandbox),
      open registration.
- [ ] `/organizer/t/<slug>/` public page loads; register a team from an
      incognito window; approve it; generate fixtures; enter a score; standings
      update with the correct points (football 3/1/0, cricket 2/1/0).

---

## 10. Backups & operations ➕

- [ ] Automated **daily Postgres backups** (managed DB snapshot or `pg_dump` cron),
      with a tested restore.
- [ ] `media/` included in backups (or on durable object storage).
- [ ] Error logging/monitoring (e.g. Sentry) and uptime checks.
- [ ] Log rotation for Gunicorn/nginx.

---

## 11. Repo hygiene (one-time) 🧹

From an environment where `git push` works (the managed session here pushes via
the GitHub API, which can't bulk-delete), untrack the files that slipped in
before `.gitignore`:

```bash
git rm -r --cached --quiet $(git ls-files | grep -E '\.pyc$|__pycache__|esports/media/')
git commit -m "Untrack committed pyc and media files"
git push
```

- [ ] Stale `.pyc`/`__pycache__`/`media` files removed from the repo.

---

## Quick paths by host

**PaaS (Railway / Render / Fly)** — fastest:
1. Add `psycopg2-binary`, `gunicorn`, `whitenoise` to `requirements.txt`.
2. Apply the settings changes in steps 2–4.
3. Set all env vars in the dashboard; attach a managed Postgres.
4. Start command: `gunicorn esports.wsgi --chdir esports`.
5. Run `migrate` + `collectstatic` as a release/deploy hook.

**VPS (Ubuntu + nginx + systemd)**:
1. Postgres + a system user + virtualenv install.
2. Gunicorn under systemd; nginx reverse proxy with TLS and `/static/` + `/media/`.
3. Env vars in the systemd unit (`EnvironmentFile=`).

---

**Bottom line:** the application is feature-complete and tested. Going live is
the settings/infra work above — the biggest items are **Postgres (step 2)**,
**static/media (step 3)**, **security settings (step 4)**, and a **bKash sandbox
test (step 6)** before taking real payments.
