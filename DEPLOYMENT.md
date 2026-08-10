# Production Deployment Checklist — D167 Tournament Platform

This is the practical, project-specific checklist to take D167 from
"works and tested locally" to "real organizers using it." Work top to bottom;
each step says **what to do** and **why**.

> **Legend:** ✅ already handled in the code · ⚙️ needs a settings/config change ·
> ➕ needs something added (dependency, service, or infra).

> **Status:** the **code-side** work for Railway is **already applied** —
> `DATABASE_URL`/Postgres (`dj-database-url`), WhiteNoise static, `STATIC_ROOT`,
> production security block, `RAILWAY_PUBLIC_DOMAIN` trust, env-configurable
> `MEDIA_ROOT`, a production-safe media route, `Procfile`, `runtime.txt`, and the
> deploy dependencies in `requirements.txt`. Follow **"Deploy to Railway"**
> below for the click-path. The numbered sections 0–11 are the general reference
> (and cover VPS/other hosts) — for Railway their ⚙️/➕ code items are done.

---

## Deploy to Railway (recommended — code already wired) 🚂

Everything the app needs for Railway is in the repo. This is the click-path.

### 1. Create the project
- [ ] Push this branch to GitHub (already there).
- [ ] Railway → **New Project → Deploy from GitHub repo** → pick this repo and
      the deployment branch.
- [ ] Railway auto-detects Python and uses the **`Procfile`**:
      - `release:` runs `migrate` + `collectstatic` on every deploy
      - `web:` runs `gunicorn esports.wsgi:application` bound to `$PORT`

### 2. Add PostgreSQL
- [ ] In the project, **New → Database → PostgreSQL**.
- [ ] Railway injects **`DATABASE_URL`** into the app service automatically — the
      settings pick it up via `dj-database-url` (no manual DB config needed).

### 3. Set environment variables (app service → Variables)

| Variable | Value | Notes |
|----------|-------|-------|
| `DJANGO_SECRET_KEY` | *(generate)* | `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"` |
| `DJANGO_DEBUG` | `False` | |
| `DJANGO_ALLOWED_HOSTS` | your custom domain(s) | the `*.up.railway.app` domain is trusted automatically via `RAILWAY_PUBLIC_DOMAIN` |
| `TOURNAMENT_FEE` | e.g. `500` | BDT; `0` = free/auto-waived |
| `DJANGO_DEFAULT_FROM_EMAIL` | `D167 <no-reply@yourdomain>` | |
| `DJANGO_EMAIL_BACKEND` + SMTP vars | *(when going live)* | see section 5; until then emails print to logs |
| `BKASH_ENABLED` / `BKASH_*` | *(when going live)* | start with sandbox; see section 6 |

- [ ] `DATABASE_URL` is present (from the Postgres plugin) — do **not** set it by hand.
- [ ] `PORT` is provided by Railway automatically — do **not** set it.

### 4. Persist uploaded media (organizer/team logos) — recommended
Container disks are ephemeral, so uploads vanish on redeploy unless stored on a volume.
- [ ] App service → **Volumes → New Volume**, mount path e.g. `/data/media`.
- [ ] Set variable **`MEDIA_ROOT=/data/media`** (settings already read this).
- [ ] (Skip only if you don't accept image uploads yet; you can add it later.)

### 5. Deploy & initialise
- [ ] Trigger the deploy. Watch logs: the `release` step should run migrations
      (seeding **Turf Football** + **Cricket**) and `collectstatic`.
- [ ] Open a shell (Railway → service → **Shell**, or `railway run`) and create
      the admin user:
      ```bash
      cd esports && python manage.py createsuperuser
      ```
      (Log in with a **phone number** — that's the username field.)
- [ ] In `/admin/`, create one **`SiteInfo`** row so the public esports theme
      renders its header/nav.

### 6. Domain & HTTPS
- [ ] Use the generated `*.up.railway.app` URL, or add a **custom domain**
      (Settings → Domains) and put it in `DJANGO_ALLOWED_HOSTS`.
- [ ] HTTPS is automatic on Railway; the app is already proxy-aware
      (`SECURE_PROXY_SSL_HEADER`), so `SECURE_SSL_REDIRECT` and the bKash
      `https://` callback work correctly.

### 7. Smoke-test the live site
- [ ] `/organizer/signup/` → create an organizer → dashboard loads **with CSS**
      (confirms WhiteNoise/`collectstatic` worked).
- [ ] Create a football **and** a cricket tournament → **Pay** (bKash sandbox, or
      set `TOURNAMENT_FEE=0` to auto-waive) → open registration.
- [ ] From an incognito window, open `/organizer/t/<slug>/`, register a team,
      approve it, generate fixtures, enter a score → standings update with the
      right points (football 3/1/0, cricket 2/1/0).

### 8. Before real payments / real email
- [ ] Do the **bKash sandbox** transaction (section 6 of the checklist), then
      switch `BKASH_BASE_URL` + credentials to live.
- [ ] Set the **SMTP** variables (section 5) and send a test registration email.

> **Backups:** enable Railway's Postgres backups (or a scheduled `pg_dump`) and
> ensure the media volume is included — see section 10.

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

> **Already applied in this repo:** `requirements.txt` includes `psycopg2-binary`
> and `dj-database-url`, and `settings.py` reads `DATABASE_URL` (falling back to
> SQLite locally). The snippet below documents what was done / how to do it
> manually on another host.

**a. Add the driver** (`requirements.txt`):

```
psycopg2-binary>=2.9
dj-database-url>=1.3
```

**b. Make `DATABASES` env-driven** (this project uses `dj-database-url`):

```python
import dj_database_url
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
```

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

> **Already applied in this repo:** `STATIC_ROOT`, WhiteNoise middleware +
> `STATICFILES_STORAGE`, env-configurable `MEDIA_ROOT`, and a production-safe
> media route in `esports/urls.py` (works when `DEBUG=False`).

**a. `STATIC_ROOT`** (already in `esports/settings.py`):

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

**b. Static via WhiteNoise** (already wired):

```
# requirements.txt
whitenoise>=6.0
```

```python
# settings.py — right after SecurityMiddleware
"whitenoise.middleware.WhiteNoiseMiddleware",
# non-manifest compressed storage (tolerant of legacy template static refs):
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
```

**c. Media files.** `media/` is **user-uploaded** and must persist and be served.
On Railway, mount a **volume** and set `MEDIA_ROOT` to it (see the Railway
section, step 4). On a VPS, an nginx `/media/` location is ideal; object storage
(`django-storages`) is the scale-up path.

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

With `DEBUG=False` behind HTTPS, these belong in `esports/settings.py` (gated on
`not DEBUG` so local dev is unaffected).

> **Already applied in this repo:** the block below plus `CSRF_TRUSTED_ORIGINS`
> derived from `ALLOWED_HOSTS` are in `settings.py`.

```python
CSRF_TRUSTED_ORIGINS = [
    "https://" + h for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")
]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

- [ ] `python manage.py check --deploy` shows no critical warnings once a real
      `DJANGO_SECRET_KEY` is set and `DEBUG=False`.
- [ ] `CSRF_TRUSTED_ORIGINS` includes your HTTPS domain (needed for all POST
      forms — login, score entry, payments — to work behind HTTPS).
- [ ] `SECURE_PROXY_SSL_HEADER` is set (Railway/most PaaS terminate TLS at a
      proxy) so the bKash callback URL is built as `https://`.

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

Do **not** use `manage.py runserver` in production. Use Gunicorn (already in
`requirements.txt`, and the `Procfile` `web:` line runs it):

```bash
# from the esports/ directory
gunicorn esports.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

- [ ] Gunicorn added and serves the app.
- [ ] Process is supervised (Railway/PaaS process manager, or a systemd unit on
      a VPS).
- [ ] `WEB_CONCURRENCY` / `--workers` tuned to the host (2×CPU + 1 is a start).

---

## 8. Web server & TLS ⚙️➕

- [ ] HTTPS enabled with a valid certificate (automatic on Railway/most PaaS;
      Let's Encrypt via nginx/Caddy on a VPS).
- [ ] On a VPS: nginx reverse-proxies to Gunicorn and serves `/static/` and
      `/media/` directly. On Railway: WhiteNoise handles static; use a mounted
      volume for media.
- [ ] HTTP → HTTPS redirect works (also enforced by `SECURE_SSL_REDIRECT`).

---

## 9. Deploy, run & verify ✅➡️

Run these on the server (from `esports/`), in order (on Railway the `Procfile`
`release:` step runs the first two automatically):

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

**Railway** — see the **"Deploy to Railway"** section above; the code, `Procfile`,
and dependencies are already in the repo, so it's mostly clicking + env vars.

**Other PaaS (Render / Fly)** — same shape as Railway:
1. Deps (`psycopg2-binary`, `gunicorn`, `whitenoise`, `dj-database-url`) are
   already in `requirements.txt`; the settings already read `DATABASE_URL`.
2. Set env vars in the dashboard; attach a managed Postgres (`DATABASE_URL`).
3. Start command: `gunicorn esports.wsgi:application --chdir esports --bind 0.0.0.0:$PORT`.
4. Run `migrate` + `collectstatic` as a release/deploy hook (the `Procfile`
   `release:` line already does this on hosts that honour Procfiles).
5. Add `<your-host-domain>` to `DJANGO_ALLOWED_HOSTS`.

**VPS (Ubuntu + nginx + systemd)**:
1. Postgres + a system user + virtualenv install.
2. Gunicorn under systemd; nginx reverse proxy with TLS and `/static/` + `/media/`.
3. Env vars in the systemd unit (`EnvironmentFile=`).

---

**Bottom line:** the application is feature-complete and tested. Going live is
the settings/infra work above — the biggest items are **Postgres (step 2)**,
**static/media (step 3)**, **security settings (step 4)**, and a **bKash sandbox
test (step 6)** before taking real payments.
