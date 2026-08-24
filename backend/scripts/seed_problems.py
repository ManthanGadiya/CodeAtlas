"""Seed curated skills and problems into the configured database.

Usage (from backend/ with the virtual environment active):
    python -m scripts.seed_problems

Idempotent: running it again adds nothing new.
"""

from app.db.session import SessionLocal
from app.problems.seed import seed_problems


def main() -> None:
    db = SessionLocal()
    try:
        created = seed_problems(db)
        print(f"Seed complete: {created} problem(s) created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
