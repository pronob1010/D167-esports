# D167 — Tournament Hosting Platform Roadmap

**Goal:** Turn the current single-purpose demo site into a *rentable, multi-tenant
tournament platform* where any organizer can sign up, create and manage their own
tournaments professionally, starting with **turf football** and adding more games over time.

**Business model (decided):** *Fee per tournament* — an organizer pays each time they
create/run a tournament.

**Payments:** Design the data model for it now, but do **not** build the payment
integration yet. Launch free, add billing later.

---

## 1. Where we are today (honest baseline)

The project is a working Django app, but it is built as a **single-tenant demo**: it
shows *one* organization's tournaments, entered by hand through the Django admin.

**Apps:** `Accounts`, `administration`, `teams`, `players`, `matches`, `esports` (config).

**Tournament data model (in `matches/models.py`):**

```
Tournament -> MatchRound -> MatchGroup -> Match -> RegisteredTeams -> PlayersPointTable
```

This hierarchy is actually good — it can model group stages, rounds, and per-match
team/player scoring. The problem is **ownership**, not structure.

### The core gaps for "ready for rent"

| Gap | Today | Needed for a platform |
|-----|-------|----------------------|
| **Ownership / multi-tenancy** | `Tournament`, `Team`, etc. are global — no owner field | Every tournament belongs to an organizer; each organizer sees only their own data |
| **Self-service management** | Only the site admin (via Django admin) can create/run tournaments | Organizers manage everything from their own dashboard, no admin access |
| **Registration** | Teams added manually by admin | Public sign-up pages; teams register themselves |
| **Billing** | None | Organizer pays a fee per tournament created |
| **Multi-game** | Football-only, hardcoded assumptions | Game is a config/type; new games are data, not code |
| **Production safety** | `DEBUG=True`, hardcoded `SECRET_KEY`, SQLite, `ALLOWED_HOSTS=[]` | Env-based secrets, Postgres, real hosting, backups |

### What's already in our favor
- Custom `User` model (`Accounts.User`) with `sub_admin` / `player` flags and
  phone-based login — a real user system already exists.
- A flexible tournament hierarchy that supports groups, rounds, and scoring.
- An `administration` app with sponsor/site-content models we can reuse for
  per-organizer branding later.

---

## 2. The one big idea: multi-tenancy

Everything hinges on this. Right now the app answers *"show the tournaments."* It must
instead answer *"show **this organizer's** tournaments."*

Concretely, we introduce an **Organizer** (the tenant) and attach ownership to the data:

```
Organizer (the paying tenant / tournament host)
    +-- owns -> Tournaments
                   +-- Rounds -> Groups -> Matches -> Registrations
    +-- owns -> Teams / Players (scoped to their tournaments)
```

- A `User` can be an **Organizer** (hosts tournaments), a **Team captain / player**
  (registers for tournaments), or both.
- Every `Tournament` gets an `organizer` foreign key.
- Every query in organizer-facing views is filtered by the logged-in organizer, so
  **no one can see or touch another organizer's data**. This is the single most
  important rule of the whole build.

---

## 3. Proposed data model changes

New / changed models (names are provisional):

**New:**
- `Organizer` — links to a `User`; holds display name, logo, contact, slug for their
  public page, subscription/plan status.
- `Game` — a lookup table (`Turf Football`, later `Cricket`, `Valorant`, …) so new
  games are just rows. Holds game-specific config (team size, scoring style).
- `TournamentRegistration` — a team's request to join a tournament (status: pending /
  approved / rejected / paid), separate from `RegisteredTeams` (which is match-level).
- `TournamentPayment` — record of the per-tournament fee the *organizer* owes/paid.
  Built as a model now; actual payment gateway wired later.

**Changed:**
- `Tournament` — add `organizer` (FK), `game` (FK), `status`
  (draft / open / ongoing / completed), `registration_open`, `entry_fee`, dates,
  `format` (knockout / league / groups+knockout), `max_teams`.
- `Team` / `Player` — add `organizer` (or scope through tournament) so teams don't
  leak across tenants.

All changes ship as **Django migrations** so existing demo data can be preserved or
cleanly reset.

---

## 4. Phased plan

Each stage produces something usable. We do **not** build everything at once.

### Stage 0 — Cleanup & production foundation (~2–4 days)
*Make the current app safe and reproducible before adding features.*
- Move `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, DB creds to environment variables.
- Add `requirements.txt`, `.gitignore` (stop tracking `db.sqlite3`, `media/`, `.pyc`).
- Fix known bugs (e.g. `null=Team` typos, template path issues, dead code).
- Add a `README` with run instructions.
- **Deliverable:** a clean repo anyone can clone and run.

### Stage A — Multi-tenant foundation (~2–3 weeks)
*The architectural core. Nothing else works without this.*
- Add `Organizer` model + organizer signup/onboarding flow.
- Add `organizer` ownership to `Tournament` (and scope teams/players).
- Migrate to **PostgreSQL**.
- Build the **organizer dashboard shell** (login -> "your tournaments" list, empty
  for now).
- Enforce per-organizer data scoping on every query.
- **Deliverable:** organizers can sign up and log in to their own (empty) dashboard.

### Stage B — Core product: self-service tournaments (~3–5 weeks)
*The actual product. Football-only to start.*
- Organizer can, without any admin access:
  - Create a tournament (name, dates, format, max teams, entry fee).
  - Manage teams/players in it.
  - Generate fixtures / brackets (knockout + league to start).
  - Enter match scores and see standings update automatically.
  - Publish a public tournament page.
- Reuse the existing `Round -> Group -> Match` hierarchy under the hood.
- **Deliverable:** an organizer can run a real turf-football tournament end to end.

### Stage C — Public registration & go live free (~2 weeks)
*Get real users before charging anyone.*
- Public per-tournament pages with a "Register your team" form.
- Team captains sign up, submit a roster, organizer approves.
- Email/SMS notifications for registration + fixtures.
- Launch **free** with a handful of real organizers to validate demand.
- **Deliverable:** live platform, real tournaments, no payments yet.

### Stage D — Monetize: fee per tournament (~2–4 weeks)
*Turn on the "rent."*
- When an organizer publishes a tournament, they owe a fee (the `TournamentPayment`
  model built in Stage A activates here).
- Wire up a payment gateway — **local (bKash/Nagad/SSLCommerz)** or **Stripe** —
  decided at this stage based on your audience.
- Free trial / first-tournament-free option to lower the barrier.
- Organizer billing history.
- **Deliverable:** the platform earns per tournament.

### Stage E — Expand games (ongoing)
*"Day by day we add more games."*
- Because `Game` is a data row with per-game config, adding cricket, esports, etc.
  becomes mostly configuration + a few game-specific scoring rules.
- Add one game at a time based on demand.
- **Deliverable:** multi-game platform.

---

## 5. Timeline summary

| Stage | Outcome | Rough effort |
|-------|---------|-------------|
| 0. Cleanup | Safe, reproducible repo | 2–4 days |
| A. Multi-tenant foundation | Organizers sign up & log in | 2–3 weeks |
| B. Core product | Organizers run tournaments themselves | 3–5 weeks |
| C. Go live free | Public registration, real users | 2 weeks |
| D. Monetize | Fee per tournament | 2–4 weeks |
| E. Expand | More games | ongoing |

**To a paying product (Stages 0 -> D):** roughly **3–4 months** of focused work.
**To a free public launch (Stages 0 -> C):** roughly **2–2.5 months**.

---

## 6. Key decisions still open

1. **Hosting** — where the live app runs (VPS, Railway/Render, etc.). Needed by Stage A.
2. **Payment provider** — local (bKash/Nagad/SSLCommerz) vs. Stripe. Needed by Stage D.
3. **Notifications** — email, SMS, or both (SMS matters for local team captains).
4. **Fee amount / free-trial policy** — the actual per-tournament price.

---

## 7. Recommended next step

Start with **Stage 0 (cleanup & production foundation)**. It's low-risk, makes the
codebase safe to build on, and is required no matter what comes next. Stage A can begin
immediately after.

*This document is a plan for review — no application code has been changed yet.*
