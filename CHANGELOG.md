# CodeAtlas Changelog

All notable changes to CodeAtlas are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and CodeAtlas follows Semantic Versioning where applicable.

---

## [Unreleased]

### Added

- Behavior signals + learner summary API (Phases 2.5 & 2.6 backend):
  - New `behavior` domain: `behavior_observations` threshold crossings and `behavior_patterns` aggregates (Alembic `0009`). Four deterministic signals from already-persisted artifacts/executions: `REPEATED_RETRY` (≥3 failed submits since last full pass), `RANDOM_EDITING` (≥4 distinct revisions while unresolved, proxy), `LOW_TESTING` (≥3 submits with zero Runs), and `PRODUCTIVE_PERSISTENCE` (full pass after ≥2 failures). Each emits a `BEHAVIOR_OBSERVED` event and upserts a per-student pattern (Phases 2.5 & 2.6).
  - `GET /api/analytics/learner` — the learner model's first read surface: skill states (weakest-first, with `reliability` = unknown when confidence < 0.5), open mistakes, mistake patterns, and behavior patterns for the personalized dashboard to consume.
  - Tests: threshold, severity escalation, streak-reset, run-mode isolation, and learner-endpoint shape (auth + empty + populated).

- Deterministic mistake detection (ROADMAP Phase 2.2, deterministic layer of docs/Mistake_Taxonomy.md §50):
  - New mistakes domain: `mistake_categories` reference table seeded with the documented M01–M24 codes (Alembic `0008`, deterministic ids shared with runtime), a `mistakes` table linking each detection to its execution/artifact with severity, confidence, an evidence note, and a resolution lifecycle, plus `mistake_patterns` recurrence counters keyed by (student, category, skill) so one failure type aggregating across different problems becomes visible.
  - Failed submits are classified from signals the runner already produced — no LLM in this path: `COMPILE_ERROR` → M01 Syntax Error (0.95), `RUNTIME_ERROR` → M03 Runtime Error (0.85), `TIMEOUT`/`MEMORY_LIMIT` → M07 Complexity Mistake (0.65), all-visible-pass-but-hidden-fail → M10 Edge Case Failure (0.7), other wrong answers → M04 Logic Error (0.5). `SYSTEM_ERROR` is never attributed to the student.
  - Every detection emits a new server-emitted `MISTAKE_DETECTED` learning event carrying category code, severity, confidence, and the mistake id.
  - A fully passing submit resolves earlier unresolved mistakes on the same problem (taxonomy §45–46 lifecycle).
  - Compile-error submits now also carry weak negative skill evidence, closing the gap flagged when evidence wiring landed.
  - Run-mode attempts remain unclassified in V1 (exploratory practice).
  - Tests: pure classifier rules plus end-to-end submit flows covering event emission, evidence coupling, the resolution lifecycle, run-mode isolation, and cross-problem recurrence through a shared skill.

- Submission evidence wiring — completes the Phase 2.4 learning loop, so mastery now accumulates from real student activity:
  - Full-pass submits update every skill linked to the problem: first-attempt solves carry strength 1.0, retries taper to 0.7 (attempts 2–3) and 0.5 (4+); failed submits count as ambiguous negative evidence (0.4); compile/runtime/timeout outcomes as weak negatives (0.3).
  - Primary skills receive full weight and supporting skills half (docs/Data_Model.md §28); each snapshot records its reason plus the problem slug so any dashboard value stays explainable.
  - Run-mode executions never touch mastery: visible-example success cannot separate knowledge from familiarity (docs/Learning_Model.md §12.4).
  - Zero-graded-case submissions (harness-level errors) are skipped entirely rather than misattributed.
  - Tests: end-to-end submit/run flows against the fake runner asserting state creation, role weighting, failure direction, attempt counting that ignores runs, plus pure derivation-rule coverage.

- Student skill model foundation (ROADMAP Phase 2.4 begins):
  - `student_skill_states` and `mastery_snapshots` tables (Alembic `0007`): one revisable mastery belief per (student, skill) pair — mastery, confidence, retention placeholder, evidence count — plus an append-only audit trail so any value can be explained by replaying its change history.
  - Rule-based mastery update engine (`app/skills/service.py`, model version `mastery-rule-v1`) implementing Learning_Model Stage 1: each evidence observation moves mastery an exponential-moving-average step toward what it implies, scaled by evidence strength in [0, 1]; confidence rises separately as consistent signal accumulates and never gates further learning; estimates clamp to [0.02, 0.98] so no belief becomes unrevisable; every update writes a reason-bearing snapshot (docs/Learning_Model.md rules 3, 6, 12).
  - Tests covering directionality, strength scaling, convergence into the top mastery band under sustained strong evidence, single-event non-domination, floor/ceiling clamping, snapshot chaining, one-row-per-pair semantics, and rejection of malformed strength/reason input.

- Frontend skeleton — Next.js app completing Phase 1.2's UI and closing out ROADMAP Level 1:
  - Account bootstrap/login flow driven by `/api/auth/status` (single-user registration appears only while no account exists).
  - Dashboard consuming the analytics summary: totals, submit success rate, completed-problem count, per-problem progress table, recent activity feed, and a first-run empty state.
  - Problem browser and problem detail pages: statement, skills, visible examples, and starter code rendered from the catalog API.
  - In-browser code editor with Tab-key indentation wired to Run (visible examples) and Submit (all tests), with full result rendering: status badges, per-case pass/fail detail for visible cases, hidden cases shown as anonymous entries only, compile/runtime error messages, program output tails.
  - The problem page emits `PROBLEM_OPENED` into the learning-event stream on first visit.

- Evidence layer (Phases 1.4, 1.5, and the analytics backend of 1.6):
  - Learning-event stream: immutable `learning_events` table (Alembic `0006`) with a controlled event vocabulary, per-event schema versions, and an authenticated ingestion endpoint (`POST /api/events`) for client-emitted events.
  - Code version history: `code_artifacts` table (Alembic `0005`) forming a parent-linked chain per problem with SHA-256 content hashes, deduplication of identical consecutive submissions, and stored unified diffs against the previous version; executions now reference the artifact they ran.
  - Server-emitted learning events: every Run/Submit records a `CODE_RUN` event (mode, status, pass counts) and a full-pass submit additionally records `PROBLEM_COMPLETED`.
  - Analytics summary endpoint (`GET /api/analytics/summary`): honest activity observations — run/submit totals, submit success rate, problems attempted/completed, recent activity feed, and per-problem breakdown.
  - Artifact timestamps use microsecond-precision client-side defaults so same-second submissions order deterministically.

- Code execution engine (Phase 1.3):
  - Docker-isolated Python sandbox: submissions run in containers with network disabled (`--network none`), hard memory and CPU caps, PID limits plus `--init` reaping (fork-bomb protection), read-only root filesystem with a noexec/nosuid/nodev tmpfs, all capabilities dropped, `no-new-privileges`, and a non-root user. The harness is mounted read-only; code and test data travel via stdin.
  - Host-side hardening: bounded tail-keeping stream capture so output-flooding programs cannot exhaust host memory (and the trailing results block survives), explicit UTF-8 decoding immune to host locale, wall-clock timeout with forced container removal, image pre-check that fails fast outside the timeout window when the runner image is missing, and status mapping to SUCCESS / COMPILE_ERROR / RUNTIME_ERROR / TIMEOUT / MEMORY_LIMIT / SYSTEM_ERROR that trusts parsed results over exit codes.
  - Strict result comparison rejecting Python's bool/int conflation while treating ints and floats as numerically comparable.
  - Hidden-test policy enforced in code: hidden cases and their expected outputs never leave the server — a failed submit reports an anonymous pass/fail per hidden case plus the learner's own error text.
  - `POST /api/problems/{slug}/run` grades visible examples; `POST /api/problems/{slug}/submit` grades everything. Both auth-guarded and rate-limited (10/min); 503 with guidance when Docker is unavailable.
  - Every execution persisted as learning evidence (`executions`, `test_case_executions`; Alembic `0003`), plus a uniqueness guard on `(problem_id, name)` for test cases (Alembic `0004`) protecting evidence attribution.
  - Tests: harness protocol without Docker; container-flag tripwire unit tests so a weakened sandbox configuration fails CI; API behaviour via fake runner; real-container e2e (correct grading, infinite-loop kill, memory limit, network denial, read-only filesystem) auto-skipped without Docker.

- Problem catalog (Phase 1.2, part 2):
  - `skills`, `problems`, `problem_skills`, and `test_cases` tables (Alembic revision `0002`), matching the Version-1 core table set in docs/Data_Model.md §86.
  - Auth-guarded read endpoints: `GET /api/problems` (catalog) and `GET /api/problems/{slug}` (statement, starter code, skills, visible examples only — hidden evaluation tests never leave the server).
  - Five curated Python problems seeded idempotently (`python -m scripts.seed_problems`), each with visible examples plus hidden edge/boundary cases deliberately designed to expose boundary-handling behaviour for future mistake analysis.
  - Function-call evaluation contract on every problem (`function_name(*input_args) == expected_output`) ready for the Phase 1.3 sandbox.

- Authentication (Phase 1.2, part 1):
  - `students` and `auth_sessions` tables (Alembic revision `0001`) — the first database-backed module.
  - Single-user account bootstrap: registration succeeds only while no student exists, then answers 409.
  - Email + password login with Argon2id hashing, automatic rehash on parameter upgrades, and identical errors for unknown email vs wrong password.
  - Server-side sessions: opaque tokens in HttpOnly SameSite cookies, only SHA-256 hashes stored, revocation on logout.
  - In-process sliding-window rate limiting on login attempts (5/minute per IP).
  - Public `/api/auth/status` endpoint so the frontend can offer first-account creation; credentialed CORS for the Next.js origin.
  - Timing-safe login verification (constant-cost dummy hash) so account existence cannot be probed by response latency.
  - Comma-separated `CORS_ORIGINS` env parsing via pydantic-settings `NoDecode` + validator.
  - Alembic model registry (`app/db/all_models.py`) so future autogenerate sees every ORM module instead of proposing destructive drops.
  - CI job proving migrations run against real PostgreSQL (`upgrade` → `downgrade` → `upgrade`).

- Engineering foundation (ROADMAP Phase 1.1):
  - Backend application skeleton: FastAPI app factory, environment-driven configuration with safe defaults, and an `/api/healthz` liveness endpoint (`backend/app`).
  - Database layer: SQLAlchemy 2.x engine/session management and an Alembic migration baseline that reads its URL from application settings, keeping credentials out of `alembic.ini`.
  - Test suite covering configuration defaults and system endpoints; ruff lint/format toolchain plus a pre-commit configuration.
  - Docker Compose service providing PostgreSQL 16 for local development; the backend also starts without Docker or a reachable database.
  - GitHub Actions CI pipeline running lint and tests on Python 3.11–3.13 for pushes and pull requests.
  - Repository hygiene: hardened `.gitignore` and a `.env.example` template documenting all supported environment variables. AI provider keys (Gemini/Groq) are intentionally optional placeholders until the AI gateway milestone.

- Established the foundational project vision for CodeAtlas.
- Defined CodeAtlas as a personal coding intelligence and adaptive tutoring system.
- Defined the distinction between CodeAtlas and conventional AI coding assistants.
- Established the core observation → modeling → adaptation → learning loop.
- Defined the initial student scope as a single-user personal coding environment.
- Defined the core behavioral signals CodeAtlas should observe:
  - Coding activity
  - Debugging behavior
  - Time taken
  - Number of attempts
  - Errors
  - Hints requested
  - Questions asked
  - Tests written
  - Code revisions
- Defined the initial mistake taxonomy:
  - Syntax errors
  - Logic errors
  - Off-by-one errors
  - Wrong algorithms
  - Complexity mistakes
  - Requirement misunderstanding
  - Repeated mistakes
  - Solution copying
  - Overengineering
- Defined the student skill model.
- Defined the behavior model.
- Defined the adaptive curriculum concept.
- Defined the tutoring engine.
- Defined forgetting and retention modeling.
- Defined adaptive problem generation.
- Defined the AI/ML strategy.
- Defined the evaluation framework.
- Defined the data model.
- Defined security, privacy, and ethical requirements.
- Defined the long-term research-grade roadmap.
- Defined the product and system design principles.
- Established the initial documentation architecture.

### Documentation

Added the foundational specification documents:

- `docs/VISION.md`
- `docs/Problem_Statement.md`
- `docs/System_Architecture.md`
- `docs/PRD.md`
- `docs/Learning_model.md`
- `docs/mistake_taxonomy.md`
- `docs/behavior_model.md`
- `docs/Adaptive_curriculum.md`
- `docs/tutoring_engine.md`
- `docs/forgetting_and_retension.md`
- `docs/problem_generator.md`
- `docs/ai_and_ml_strategy.md`
- `docs/evaluation_framework.md`
- `docs/data_model.md`
- `docs/security_privacy_and_ethics.md`
- `docs/ROADMAP.md`
- `docs/DESIGN.md`

---

## [0.1.0] — Planned

### Planned

The first implementation milestone will establish:

- Repository structure
- Development environment
- Backend foundation
- Frontend foundation
- Database foundation
- Authentication
- Coding workspace
- Secure code execution
- Problem management
- Event collection
- Code version history
- Basic analytics

This release will establish the technical foundation required for CodeAtlas intelligence features.

---

## Release Philosophy

CodeAtlas versions should represent meaningful capabilities rather than arbitrary feature counts.

A release should ideally answer:

> "What can CodeAtlas understand or do now that it could not do before?"

Learning-system changes should additionally include evaluation evidence whenever possible.

---

[Unreleased]: https://github.com/M/codeatlas/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ManthanGadiya/CodeAtlas