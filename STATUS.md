# CodeAtlas — Project Status

> **Last Updated:** 2026-09-13  
> **Project Status:** 🟢 Levels 1, 2 & 3 Complete — Level 3 Adaptive Intelligence Shipped (3.1, 3.6, 3.4, 3.2, 3.3, 3.5, 3.7)  
> **Current Version:** 0.1.0-dev  
> **Development Stage:** ROADMAP Levels 1-3 complete; Level 3 Phases 3.1 Tutor (0013), 3.6 Retention (0014), 3.4 Curriculum (0015), 3.2 Generator (0016), 3.3 Difficulty (0017), 3.5 Retrieval (0018), 3.7 Transfer (0019 transfer_evaluations) landed  
> **Primary Objective:** Level 4 deferred per request — stabilize Level 3, harden evaluation, no RL/research-grade today.

---

# 1. Current State

ROADMAP Levels 1, 2 and 3 are complete (3.1, 3.6, 3.4, 3.2, 3.3, 3.5, 3.7). A student can register, browse seeded Python problems, **generate validated variants**, get **a personalized next-problem recommendation**, ask the tutor for socratic hints, see which skills are fading, **practice at the right difficulty**, **receive scheduled retrieval practice**, and **be tested for transfer on the same skill in a new surface** — while every execution, code version, learning event, mistake, behavior, tutor interaction, retrieval, generated problem, difficulty estimate, and transfer probe feeds the adaptive loop.

- FastAPI backend: modular monolith (auth, users, problems, execution, events, analytics, skills, mistakes, behavior, **tutor + AI gateway + retention + curriculum + generator + difficulty + retrieval + transfer**)
- Next.js frontend: login/bootstrap, dashboard (personalized learner model + **retention due + recommended next + adaptive difficulty + retrieval + transfer due**), problem browser (includes generated + transfer variants), problem detail with editor + **TutorPanel (hint ladder 0-7)**
- Docker sandboxed execution with CI-verified end-to-end tests
- Immutable learning-event stream + code artifact version chains + analytics appendix + **tutor (0013) + retention (0014) + curriculum decisions (0015) + generator fields (0016) + difficulty vectors (0017) + retrieval schedules (0018) + transfer evaluations (0019) + HINT/RETRIEVAL/CURRICULUM_DECISION/PROBLEM_GENERATED/TRANSFER_ATTEMPTED events**
- Deterministic tutoring loop: Observe → Diagnose → Minimal hint → Escalate → offline templates
- Retention engine: R(t)=exp(-t/S) with adaptive stability (×2/×0.5, caps 0.5–60d), live decay on read
- **Curriculum engine**: rule-based scorer (§55) weighting skill gap, retention due, mistake recurrence, difficulty fit, repetition penalty, prerequisite pivot — explains every choice
- **Generator engine**: validated mutation pipeline (§59: syntax → tests → solution → difficulty → duplicate fingerprint → quality ≥0.5) with three deterministic transforms, auditable provenance
- **Difficulty engine**: 6-dimensional vector + IRT P(success) + zone + target band calibrated from success_rate
- **Retrieval engine**: deliberate scheduling (§20-22: S×0.8, ×2/×0.5/×0.8), ladder recognition→transfer ramped by stability, interleaving, auto-next, RETRIEVAL_ATTEMPTED audit
- **Transfer engine**: T0-T5 ladder (§50) context_shift variants, mastery ≥0.35 eligibility, excludes recent success, auditable TRANSFER_ATTEMPTED
- GitHub Actions CI: lint + tests on Python 3.11–3.13, PostgreSQL migration reversibility, real-container sandbox e2e

## Level 1 Exit Criteria — met

The system can answer: *What did the student do? When? What code did they write? What happened when they ran it? How did their code evolve?*

## Level 2 Exit Criteria — met

The system can answer: *What does this student know? Where are they weak? What mistakes repeat? How do they behave while solving?* (learner summary weakest-first, mistake recurrence, behavior patterns, subskill hierarchy).

## Level 3.1 Exit Criteria — met

The system can answer: *What help does this student need right now, and how much is enough?* — deterministic intervention selection, Socratic hint ladder, and an auditable tutor history.

## Level 3.6 Exit Criteria — met

The system can answer: *What has the student learned but may be forgetting, when should they review it, and did retrieval succeed?* — exponential decay per skill, stability scheduling, and an overdue/due signal for the curriculum.

## Level 3.4 Exit Criteria — met

The system can answer: *What should this student practice next, why, and what alternatives were considered?* — scored curriculum candidates, prerequisite-aware repair, retention-weighted retrieval, and auditable decisions.

## Level 3.2 Exit Criteria — met

The system can answer: *Can we create a new, valid, non-duplicate problem that targets the intended skill and survives the full validation pipeline?* — fingerprint deduplication, syntax/test/solution checks, quality gate, and provenance tracking.

## Level 3.3 Exit Criteria — met

The system can answer: *At what difficulty is this problem for this student, what is their chance of success, and what difficulty should they tackle next to stay in the productive zone?* — 6-D vector, IRT logistic P(success), zone classification, and adaptive band recommendation calibrated from evidence.

## Level 3.5 Exit Criteria — met

The system can answer: *What should this student retrieve right now, at what effort, and when is the next retrieval due?* — due queue from R(t), ladder-ramped scheduling (recognition→transfer), success/failure/partial stability updates, auto-next interval, and auditable retrieval history.

## Level 3.7 Exit Criteria — met

The system can answer: *Can this student recognize and apply the same skill in a new surface/context?* — T2+ transfer variants (context_shift), mastery-gated eligibility, and auditable TRANSFER_ATTEMPTED with history excluding recent success.

## Level 3 Exit — complete

Level 3 Adaptive Intelligence is complete. The system now answers end-to-end: *what should this student practice next, why, at what difficulty, with what help, when to retrieve, and can they transfer?* — Level 4 research (temporal modeling, causal experiments, RL policy) remains deferred per AGENTS.md §4.

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
| M11 | Personalized dashboard frontend consuming learner API (Phase 2.6 UI) | 🟢 Complete |
| M12 | Session entity and session_id scoping for events/artifacts/executions/behaviors (Data_Model §9) | 🟢 Complete |
| M13 | Skill hierarchy completeness — description/domain, subskills, prerequisite graph, importance (Data_Model §25-28) | 🟢 Complete |
| M14 | Aggregate student state + preferences + snapshot/observation confidence (Data_Model §7, §8, §31, §38) | 🟢 Complete |
| M15 | Tutoring engine (Phase 3.1) — AI gateway + deterministic hint ladder 0-7 + TutorInteraction audit + HINT_REQUESTED/SHOWN events + TutorPanel (Data_Model §43, Tutoring_Engine.md) | 🟢 Complete |
| M16 | Retention & forgetting model (Phase 3.6) — R(t)=exp(-t/S), stability 0.5–60d, RETRIEVAL_ATTEMPTED events, GET /retention/overview + POST /retention/review, dashboard due list (Data_Model §49, Forgetting §25, §51-54) | 🟢 Complete |
| M17 | Adaptive curriculum (Phase 3.4) — rule-based scorer (§55) + prerequisite pivot, GET /curriculum/next + /decisions, dashboard Recommended next card (Data_Model §53-54, Adaptive_Curriculum §17, §55) | 🟢 Complete |
| M18 | Problem generator (Phase 3.2) — validated mutation pipeline (§59: syntax/test/solution/difficulty/duplicate/quality), 3 mutations (boundary/constraint/context), POST /generator/mutate + /generate + /validate-draft, fingerprint dedup + provenance (Data_Model §21-22, Problem_Generator §68-69, 0016) | 🟢 Complete |
| M19 | Adaptive difficulty (Phase 3.3) — 6-D vector (conceptual/implementation/reasoning/debugging/constraints/transfer), IRT P(success)=logistic(mastery-difficulty), zone + target band (productive 0.55-0.85), calibration history (Data_Model §23-24, Problem_Generator §14-18, 0017) | 🟢 Complete |
| M20 | Retrieval practice (Phase 3.5) — deliberate scheduling (§20-22, S×0.8), ladder (recognition→transfer by stability), interleaving, auto-next, GET /retrieval/due + POST /retrieval/schedule|complete + history (Forgetting §34, §51-52, 0018 retrieval_schedules) | 🟢 Complete |
| M21 | Transfer evaluation (Phase 3.7) — T0-T5 ladder (§50) via context_shift/boundary/constraint mutations, mastery ≥0.35 eligibility, excludes recent success, POST /transfer/schedule + /complete + due + history (Problem_Generator §49-51, 0019 transfer_evaluations) | 🟢 Complete |
| M22 | Level 3 complete — all Level 3 phases (3.1, 3.6, 3.4, 3.2, 3.3, 3.5, 3.7) landed, verified, docs synced | 🟢 Complete |

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
- Retention was a nullable placeholder; now computed via R(t)=exp(-t/S) per skill (Phase 3.6) and mirrored to StudentSkillState.retention, but encoding-strength factors (§8-9) and personalized per-skill forgetting rates (§16) remain future work.
- Problem generation is mutation-only (3 deterministic variants from curated seeds); LLM free-form generation remains future work — the pipeline is ready to plug a provider behind the validator. Difficulty calibration from real cohort signals (§86-87) remains dampened single-student; cohort Bayesian calibration is future work.
- Retrieval scheduling is rule-based (due = prob<0.6 or overdue + 2 weakest interleaved); importance-weighted retention priority (§26) and interleaved micro-retrieval (§67) remain stubbed; spaced-repetition baselines (Leitner/Half-Life) await evaluation.
- Transfer evaluation is single-skill T2 via generator `context_shift`; higher levels (T4 hidden technique, T5 multi-concept) and cross-skill transfer graphs remain future work; transfer history is local, not yet calibration-weighted into mastery.
- Attempt counting treats every prior submit as an attempt regardless of how much the code changed between tries — revision-aware attempt semantics are still future work.
- Behavior signals are conservative threshold crossings (e.g., random-editing proxied by revision count while unresolved — healthy iterative refinement needs diff-content analysis); severity/confidence are initial assumptions.
- `behavior_observations`/`behavior_patterns` are derived, not ground truth — trend stays `UNKNOWN` in V1.
- Event ingestion idempotency is deferred: a client retry of `POST /api/events` double-counts (no client-supplied idempotency key yet).
- Analytics loads full execution history per request — fine at Phase 1.6 scale, switch to SQL aggregates when history grows.
- Frontend not scaffolded yet (Next.js decision frozen; next milestone).
- Unit tests run on SQLite; PostgreSQL behavior is exercised by the CI migration job (`upgrade` → `downgrade` → `upgrade`) but not yet by API integration tests.
- Dependency constraints live in `pyproject.toml`; a pinned lockfile is still to be introduced.
- C++ execution deferred by product decision; Python-only for now.
- Documentation housekeeping pending: `Forgeting_And_Retention.md` filename spelling, lowercase filename references in CHANGELOG, `LICENCE` link in README, garbled fragments in VISION.md / Problem_Statement.md.

## 5. Next Step

Level 3 (0019) is complete — all 7 Level 3 phases landed, 10 retrieval + 10 transfer tests passing, frontend build green. Per your request, **Level 4 (unified model, temporal modeling, causal experiments, RL policy, etc.) is deferred today.** Next when you resume: Level 4.1 Unified Student Model + evaluation hardening per ROADMAP. No further code until you say `continue`.
