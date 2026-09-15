"""Seed curated skills and problems into the configured database.

Usage (from backend/ with the virtual environment active):
    python -m scripts.seed_problems

Idempotent: running it again adds nothing new.
"""

from app.db.session import SessionLocal
from app.problems.seed import seed_problems


def main() -> None:
    from sqlalchemy.exc import ProgrammingError

    db = SessionLocal()
    try:
        created = seed_problems(db)
        print(f"Seed complete: {created} problem(s) created.")
    except ProgrammingError as exc:
        orig = getattr(exc, "orig", None)
        detail = str(orig) if orig is not None else str(exc)
        if "fingerprint" in detail or "retention_states" in detail or "does not exist" in detail:
            print(f"Database schema out of date — run: alembic upgrade head\nDetail: {detail}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
