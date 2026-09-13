"""0016 — generator fields (ROADMAP Phase 3.2, Problem_Generator §59-69).

Adds provenance / deduplication / quality columns to `problems` so
generated and mutated problems are distinguishable, versioned via
fingerprint, and auditable. Also seeds fingerprints for existing curated
rows so future duplicate checks cover the catalog.

Revision ID: 0016
Revises: 0015
Create Date: 2026-09-13
"""

import hashlib

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def _fp(title: str, description: str, function_name: str, difficulty: str) -> str:
    raw = f"{title}\n{description}\n{function_name}\n{difficulty}".lower().strip().encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def upgrade() -> None:
    op.add_column("problems", sa.Column("fingerprint", sa.String(length=64), nullable=True))
    op.add_column("problems", sa.Column("parent_problem_id", sa.Uuid(), nullable=True))
    op.add_column("problems", sa.Column("generation_metadata", sa.JSON(), nullable=True))
    op.add_column("problems", sa.Column("quality_score", sa.Float(), nullable=True))
    op.create_index("ix_problems_fingerprint", "problems", ["fingerprint"])
    op.create_foreign_key(
        "fk_problems_parent",
        "problems",
        "problems",
        ["parent_problem_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # Backfill fingerprints for existing curated problems
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id, title, description, function_name, difficulty FROM problems")
    ).fetchall()
    for r in rows:
        fp = _fp(r.title, r.description, r.function_name, r.difficulty)
        conn.execute(
            sa.text("UPDATE problems SET fingerprint = :fp WHERE id = :id"),
            {"fp": fp, "id": str(r.id)},
        )


def downgrade() -> None:
    op.drop_constraint("fk_problems_parent", "problems", type_="foreignkey")
    op.drop_index("ix_problems_fingerprint", table_name="problems")
    op.drop_column("problems", "quality_score")
    op.drop_column("problems", "generation_metadata")
    op.drop_column("problems", "parent_problem_id")
    op.drop_column("problems", "fingerprint")
