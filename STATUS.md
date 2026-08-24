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
| M2 | Application skeleton — auth, problems, editor (Phase 1.2) | 🟡 In Progress |
| M3 | Secure Python code execution sandbox (Phase 1.3) | 🔴 Not Started |
| M4 | Event tracking system (Phase 1.4) | 🔴 Not Started |
| M5 | Code versioning (Phase 1.5) | 🔴 Not Started |
| M6 | Basic analytics dashboard (Phase 1.6) | 🔴 Not Started |

## 3. Status Legend

🟢 Complete

🟡 In Progress

🔵 Planned

🔴 Not Started

⚠️ Blocked

## 4. Known Limitations

- Phase 1.2 partially complete: authentication works; problems, editor, and dashboard are not started.
- Login rate limiting is in-process only (single deployment); shared-state limiting is required before any public exposure. Its per-IP event map also grows unboundedly and keys on direct client IP — behind a reverse proxy everyone shares one bucket.
- Sessions are static 7-day cookies; refresh-token rotation (security doc §7) is deferred.
- Expired `auth_sessions` rows are revoked/checked but never purged; a cleanup sweep is pending.
- `SameSite=Lax` cookies are the current CSRF control; a dedicated CSRF token should be evaluated when the app is exposed beyond localhost.
- No product features yet beyond authentication: no problems, editor, execution, events, or student model.
- Frontend not scaffolded yet (Next.js decision frozen; arrives within Phase 1.2).
- Unit tests run on SQLite; PostgreSQL behavior is exercised by the CI migration job (`upgrade` → `downgrade` → `upgrade`) but not yet by API integration tests.
- Dependency constraints live in `pyproject.toml`; a pinned lockfile is still to be introduced.
- Code execution sandbox not started; when it is, student code must never run on the application host.
- Documentation housekeeping pending: `Forgeting_And_Retention.md` filename spelling, lowercase filename references in CHANGELOG, `LICENCE` link in README, garbled fragments in VISION.md / Problem_Statement.md.

## 5. Next Step

Continue Phase 1.2 — Problem catalog: Skill / Problem / ProblemSkill / TestCase entities (migration 0002), curated seed problems in Python, and auth-guarded list/detail endpoints.
