"""0019 — transfer evaluations (Phase 3.7, Problem_Generator §49-51).

Revision ID: 0019
Revises: 0018
Create Date: 2026-09-13
"""

import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transfer_evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("source_problem_id", sa.Uuid(), nullable=True),
        sa.Column("transfer_problem_id", sa.Uuid(), nullable=False),
        sa.Column("transfer_level", sa.String(length=8), server_default="T2", nullable=False),
        sa.Column("result", sa.String(length=16), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "model_version", sa.String(length=32), server_default="transfer-rule-v1", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_problem_id"], ["problems.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transfer_problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transfer_student", "transfer_evaluations", ["student_id"])
    op.create_index("ix_transfer_skill", "transfer_evaluations", ["skill_id"])


def downgrade() -> None:
    op.drop_index("ix_transfer_skill", table_name="transfer_evaluations")
    op.drop_index("ix_transfer_student", table_name="transfer_evaluations")
    op.drop_table("transfer_evaluations")
