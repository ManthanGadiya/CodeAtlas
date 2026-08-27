"""0009 — behavior observations and patterns

Behavioral signal tables per docs/Data_Model.md §38-40 and
docs/ROADMAP.md Phase 2.5. Observations record threshold crossings;
patterns aggregate them per (student, behavior_type). Both name the
rule version that produced them (docs/Data_Model.md §47).

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-26
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "behavior_observations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("problem_id", sa.Uuid(), nullable=False),
        sa.Column("behavior_type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("detail", sa.JSON(), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_behavior_observations_student_id", "behavior_observations", ["student_id"])
    op.create_index("ix_behavior_observations_problem_id", "behavior_observations", ["problem_id"])

    op.create_table(
        "behavior_patterns",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("behavior_type", sa.String(length=32), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("trend", sa.String(length=16), server_default="UNKNOWN", nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "last_observed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "behavior_type"),
    )


def downgrade() -> None:
    op.drop_table("behavior_patterns")
    op.drop_index("ix_behavior_observations_problem_id", table_name="behavior_observations")
    op.drop_index("ix_behavior_observations_student_id", table_name="behavior_observations")
    op.drop_table("behavior_observations")
