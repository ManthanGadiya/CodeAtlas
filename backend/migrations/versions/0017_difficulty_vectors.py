"""0017 — difficulty vectors (Phase 3.3, Data_Model §23-24).

Revision ID: 0017
Revises: 0016
Create Date: 2026-09-13
"""

import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "problem_difficulties",
        sa.Column("problem_id", sa.Uuid(), nullable=False),
        sa.Column("overall", sa.Float(), nullable=False),
        sa.Column("conceptual", sa.Float(), nullable=False),
        sa.Column("implementation", sa.Float(), nullable=False),
        sa.Column("reasoning", sa.Float(), nullable=False),
        sa.Column("debugging", sa.Float(), nullable=False),
        sa.Column("constraints", sa.Float(), nullable=False),
        sa.Column("transfer", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="0.6", nullable=False),
        sa.Column(
            "model_version",
            sa.String(length=32),
            server_default="difficulty-rule-v1",
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("problem_id"),
    )
    op.create_table(
        "difficulty_calibrations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("problem_id", sa.Uuid(), nullable=False),
        sa.Column("old_overall", sa.Float(), nullable=False),
        sa.Column("new_overall", sa.Float(), nullable=False),
        sa.Column("reason", sa.String(length=256), nullable=False),
        sa.Column(
            "model_version",
            sa.String(length=32),
            server_default="difficulty-rule-v1",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_difficulty_calibrations_problem", "difficulty_calibrations", ["problem_id"])
    # Seed difficulty vectors for curated problems (expert-authored)
    conn = op.get_bind()
    # Hardcoded vectors mirror difficulty/service.py VECTORS
    vectors = {
        "two-sum": (0.29, 0.3, 0.3, 0.35, 0.2, 0.25, 0.2),
        "valid-palindrome": (0.30, 0.35, 0.3, 0.3, 0.25, 0.2, 0.3),
        "valid-parentheses": (0.34, 0.4, 0.35, 0.4, 0.35, 0.2, 0.25),
        "maximum-subarray": (0.57, 0.6, 0.5, 0.65, 0.45, 0.5, 0.55),
        "binary-search-first-occurrence": (0.57, 0.6, 0.55, 0.65, 0.6, 0.4, 0.5),
    }
    for slug, vals in vectors.items():
        row = conn.execute(
            sa.text("SELECT id FROM problems WHERE slug = :slug"), {"slug": slug}
        ).fetchone()
        if row:
            overall, c, impl, r, d, cons, t = vals
            conn.execute(
                sa.text(
                    "INSERT INTO problem_difficulties (problem_id, overall, conceptual, implementation, reasoning, debugging, constraints, transfer, confidence, model_version) VALUES (:pid, :o, :c, :impl, :r, :d, :cons, :t, 0.65, 'difficulty-rule-v1')"  # noqa: E501
                ),
                {
                    "pid": str(row[0]),
                    "o": overall,
                    "c": c,
                    "impl": impl,
                    "r": r,
                    "d": d,
                    "cons": cons,
                    "t": t,
                },
            )


def downgrade() -> None:
    op.drop_index("ix_difficulty_calibrations_problem", table_name="difficulty_calibrations")
    op.drop_table("difficulty_calibrations")
    op.drop_table("problem_difficulties")
