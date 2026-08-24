# CodeAtlas Changelog

All notable changes to CodeAtlas are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and CodeAtlas follows Semantic Versioning where applicable.

---

## [Unreleased]

### Added

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