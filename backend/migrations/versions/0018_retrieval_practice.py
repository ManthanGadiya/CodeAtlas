"""0018 — retrieval practice (Phase 3.5, Forgetting §51-52).

Revision ID: 0018
Revises: 0017
Create Date: 2026-09-13
"""

import sqlalchemy as sa
from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "retrieval_schedules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("problem_id", sa.Uuid(), nullable=True),
        sa.Column("ladder_level", sa.String(length=24), server_default="recall", nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False),
        sa.Column("result", sa.String(length=16), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("time_taken_ms", sa.Integer(), nullable=True),
        sa.Column(
            "model_version",
            sa.String(length=32),
            server_default="retrieval-rule-v1",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_retrieval_schedules_student", "retrieval_schedules", ["student_id"])
    op.create_index("ix_retrieval_schedules_due", "retrieval_schedules", ["scheduled_for"])
    op.create_index("ix_retrieval_schedules_skill", "retrieval_schedules", ["skill_id"])


def downgrade() -> None:
    op.drop_index("ix_retrieval_schedules_skill", table_name="retrieval_schedules")
    op.drop_index("ix_retrieval_schedules_due", table_name="retrieval_schedules")
    op.drop_index("ix_retrieval_schedules_student", table_name="retrieval_schedules")
    op.drop_table("retrieval_schedules")
