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
| M2 | Application skeleton — auth, problems, editor (Phase 1.2) | 🔵 Planned |
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

- No product features yet: no authentication, problems, editor, execution, events, or student model.
- Frontend not scaffolded yet (Next.js decision frozen; arrives with Phase 1.2).
- Database layer is unexercised by API endpoints until the first ORM models land.
- CI executes tests on SQLite; PostgreSQL integration tests arrive with the first models and an `alembic upgrade head` CI step.
- Dependency constraints live in `pyproject.toml`; a pinned lockfile is still to be introduced.
- Code execution sandbox not started; when it is, student code must never run on the application host.
- Documentation housekeeping pending: `Forgeting_And_Retention.md` filename spelling, lowercase filename references in CHANGELOG, `LICENCE` link in README, garbled fragments in VISION.md / Problem_Statement.md.

## 5. Next Step

Phase 1.2 — Application Skeleton: Next.js frontend scaffold, single-user email+password authentication (Argon2id), problem entity as the first DB-backed module, and a minimal in-browser code editor wired to a health-checked API.
