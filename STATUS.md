# CodeAtlas — Project Status

> **Last Updated:** 2026-08-27  
> **Project Status:** 🟢 Level 1 Complete — Level 2 (Personalization) In Progress  
> **Current Version:** 0.1.0-dev  
> **Development Stage:** ROADMAP Phases 1.1–1.6, 2.2, 2.4, 2.5 and 2.6 (backend) implemented  
> **Primary Objective:** Frontend consumption of the learner API and Phase 2 hardening (no Phase 3 today).

---

# 1. Current State

ROADMAP Level 1 is complete. A student can register, browse seeded Python problems, write code in the browser, execute it inside a Docker-isolated sandbox against visible examples (Run) or all tests including hidden ones (Submit), and watch an honest dashboard of what was observed — while every execution, code version, and learning event accumulates as evidence for the intelligence layers to come.

- FastAPI backend: modular monolith (auth, users, problems, execution, events, analytics modules)
- Next.js frontend: login/bootstrap, dashboard, problem browser, problem detail with editor
- Docker sandboxed execution with CI-verified end-to-end tests
- Immutable learning-event stream + code artifact version chains + analytics summary
- GitHub Actions CI: lint + tests on Python 3.11–3.13, PostgreSQL migration reversibility, real-container sandbox e2e

## Level 1 Exit Criteria — met

The system can answer: *What did the student do? When? What code did they write? What happened when they ran it? How did their code evolve?*

## 2. Milestone Tracker

| Milestone | Scope | Status |
| --------- | ---------------------------------------------------- | ------------- |
| M0 | Foundation specification (`docs/`) | 🟢 Complete |
| M1 | Engineering foundation (Phase 1.1) | 🟢 Complete |
| M2 | Application skeleton — auth, problems, editor (Phase 1.2) | 🟢 Complete |
| M3 | Secure Python code execution sandbox (Phase 1.3) | 🟢 Complete; C++ deferred by decision |
| M4 | Event tracking system (Phase 1.4) | 🟢 Complete |
| M5 | Code versioning (Phase 1.5) | 🟢 Complete |
| M6 | Basic analytics dashboard (Phase 1.6) | 🟢 Complete |
| M7 | Student skill-state tables + rule-based mastery engine (Phase 2.4 begins) | 🟢 Complete |
| M8 | Submission evidence wiring into mastery states (Phase 2.4 completes) | 🟢 Complete |
| M9 | Deterministic mistake detection: taxonomy, classification, recurrence (Phase 2.2, deterministic layer) | 🟢 Complete |
| M10 | Behavior signals + learner summary API (Phases 2.5 & 2.6 backend) | 🟢 Complete |

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
- Per-execution memory usage is not yet measured (`memory_bytes` stays NULL); container-level accounting needs `docker stats` or runtime metrics.
- Rate limiting (login and execution limiters) is in-process only; their per-IP event maps grow unboundedly and key on direct client IP — behind a reverse proxy everyone shares one bucket.
- Sessions are static 7-day cookies; refresh-token rotation (security doc §7) is deferred.
- Expired `auth_sessions` rows are revoked/checked but never purged; a cleanup sweep is pending.
- `SameSite=Lax` cookies are the current CSRF control; a dedicated CSRF token should be evaluated when the app is exposed beyond localhost.
- Frontend is a functional skeleton: plain-textarea editor (Monaco/CodeMirror arrives when needed), no frontend test suite yet (build + ESLint are the gate; Playwright e2e planned).
- Mistake detection classifies at most one primary category per submission from runner signals only; multi-label classification and code-level categories (Off-by-One M05, Wrong Algorithm M06, ...) need AST analysis and the future AI-assisted layer (taxonomy §50).
- Run-mode attempts are never classified — exploratory practice is out of scope for V1 detection.
- Mistake severity/confidence values and pattern-confidence growth are explicit initial assumptions, not validated constants.
- Evidence weights (attempt taper 1.0/0.7/0.5, failed-submit 0.4, error-outcome 0.3, supporting-role ×0.5) are explicit initial assumptions too; both weight families need evaluation against simple baselines (docs/Evaluation_Framework.md).
- Retention is stored as a nullable placeholder on skill state; no decay model computes it yet.
- Attempt counting treats every prior submit as an attempt regardless of how much the code changed between tries — revision-aware attempt semantics are still future work.
- Behavior signals are conservative threshold crossings (e.g., random-editing proxied by revision count while unresolved — healthy iterative refinement needs diff-content analysis); severity/confidence are initial assumptions.
- `behavior_observations`/`behavior_patterns` are derived, not ground truth — trend stays `UNKNOWN` in V1.
- Event ingestion idempotency is deferred: a client retry of `POST /api/events` double-counts (no client-supplied idempotency key yet).
- `session_id` documented on events/artifacts is deferred until a Session entity exists; schema_version supports the migration.
- Analytics loads full execution history per request — fine at Phase 1.6 scale, switch to SQL aggregates when history grows.
- Frontend not scaffolded yet (Next.js decision frozen; next milestone).
- Unit tests run on SQLite; PostgreSQL behavior is exercised by the CI migration job (`upgrade` → `downgrade` → `upgrade`) but not yet by API integration tests.
- Dependency constraints live in `pyproject.toml`; a pinned lockfile is still to be introduced.
- C++ execution deferred by product decision; Python-only for now.
- Documentation housekeeping pending: `Forgeting_And_Retention.md` filename spelling, lowercase filename references in CHANGELOG, `LICENCE` link in README, garbled fragments in VISION.md / Problem_Statement.md.

## 5. Next Step

Level 2 backend is feature-complete for now (no Phase 3 today). Next is the frontend slice of 2.6 — a personalized dashboard page consuming `GET /api/analytics/learner` to show skill states, open mistakes, and behavior patterns — plus hardening and evaluation of the new signals.
