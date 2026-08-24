# CodeAtlas — Project Status

> **Last Updated:** 2026-08-24  
> **Project Status:** 🟡 Engineering Foundation Complete — Implementation Begun  
> **Current Version:** 0.1.0-dev  
> **Development Stage:** ROADMAP Phase 1.1 done; Phase 1.2 next  
> **Primary Objective:** Build the first executable vertical slice on top of a reliable foundation.

---

# 1. Current State

The specification phase (Milestone 0) is complete: all foundational documents under `docs/` are established.

ROADMAP Phase 1.1 (Engineering Foundation) is implemented:

- FastAPI backend skeleton with modular-monolith boundaries (`backend/app`)
- Environment-driven configuration with safe defaults; AI provider keys optional (`docs/PRD.md` NFR-002)
- SQLAlchemy 2.x database layer and Alembic migrations baseline
- Test suite (configuration + system endpoints), ruff lint/format toolchain, pre-commit config
- GitHub Actions CI running lint and tests across Python 3.11–3.13
- Docker Compose PostgreSQL for local development — Docker is convenient, not required
- Hardened `.gitignore`; `.env.example` documents every supported variable

## 2. Milestone Tracker

| Milestone | Scope | Status |
| --------- | ---------------------------------------------------- | ------------- |
| M0 | Foundation specification (`docs/`) | 🟢 Complete |
| M1 | Engineering foundation (Phase 1.1) | 🟢 Complete |
| M2 | Application skeleton — auth, problems, editor (Phase 1.2) | 🟡 Backend complete; Next.js UI in progress |
| M3 | Secure Python code execution sandbox (Phase 1.3) | 🟢 Python complete; C++ deferred by decision |
| M4 | Event tracking system (Phase 1.4) | 🟢 Complete |
| M5 | Code versioning (Phase 1.5) | 🟢 Complete |
| M6 | Basic analytics dashboard (Phase 1.6) | 🟡 Backend summary API done; dashboard UI in progress |

## 3. Status Legend

🟢 Complete

🟡 In Progress

🔵 Planned

🔴 Not Started

⚠️ Blocked

## 4. Known Limitations

- Phase 1.2 partially complete: authentication and the problem catalog work; the editor UI and dashboard are not started.
- Sandbox trust model (V1, personal tool): harness and student code share one container process, so the single student could forge their own results; acceptable while CodeAtlas is single-user self-improvement, must be revisited for any multi-user/graded scenario.
- Hidden-test policy decision: hidden cases and their expected outputs never leave the server; a failed submit reports only an anonymous pass/fail per hidden case plus the learner's own error text. This protects generalisation evidence from being hardcoded away.
- Rate limiting (login and execution limiters) is in-process only; their per-IP event maps grow unboundedly and key on direct client IP — behind a reverse proxy everyone shares one bucket.
- Per-execution memory usage is not yet measured (`memory_bytes` stays NULL); container-level accounting needs `docker stats` or runtime metrics.
- Rate limiting (login and execution limiters) is in-process only; their per-IP event maps grow unboundedly and key on direct client IP — behind a reverse proxy everyone shares one bucket.
- Sessions are static 7-day cookies; refresh-token rotation (security doc §7) is deferred.
- Expired `auth_sessions` rows are revoked/checked but never purged; a cleanup sweep is pending.
- `SameSite=Lax` cookies are the current CSRF control; a dedicated CSRF token should be evaluated when the app is exposed beyond localhost.
- No learning intelligence yet: the event stream, artifacts, and analytics are observations only — mistake detection and the learner model are future phases.
- Event ingestion idempotency is deferred: a client retry of `POST /api/events` double-counts (no client-supplied idempotency key yet).
- `session_id` documented on events/artifacts is deferred until a Session entity exists; schema_version supports the migration.
- Analytics loads full execution history per request — fine at Phase 1.6 scale, switch to SQL aggregates when history grows.
- Frontend not scaffolded yet (Next.js decision frozen; next milestone).
- Unit tests run on SQLite; PostgreSQL behavior is exercised by the CI migration job (`upgrade` → `downgrade` → `upgrade`) but not yet by API integration tests.
- Dependency constraints live in `pyproject.toml`; a pinned lockfile is still to be introduced.
- C++ execution deferred by product decision; Python-only for now.
- Documentation housekeeping pending: `Forgeting_And_Retention.md` filename spelling, lowercase filename references in CHANGELOG, `LICENCE` link in README, garbled fragments in VISION.md / Problem_Statement.md.

## 5. Next Step

Finish Phase 1.2 — Next.js frontend skeleton with login/account-bootstrap flow, problem list/detail pages, and a Run/Submit-capable code editor wired to the new execution endpoints.
