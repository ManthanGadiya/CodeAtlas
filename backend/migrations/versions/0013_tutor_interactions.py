"""0013 — tutor interactions (ROADMAP Phase 3.1, docs/Tutoring_Engine.md).

Append-only audit trail of every hint/explanation the tutor delivers,
including the AI gateway bookkeeping so interventions can be evaluated
(Tutoring_Engine.md §48-50, Data_Model.md §43).

Revision ID: 0013
Revises: 0012
Create Date: 2026-09-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tutor_interactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("problem_id", sa.Uuid(), nullable=True),
        sa.Column("interaction_type", sa.String(length=24), server_default="HINT", nullable=False),
        sa.Column("hint_level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("intervention", sa.String(length=32), server_default="HINT", nullable=False),
        sa.Column("model_provider", sa.String(length=32), server_default="dummy", nullable=False),
        sa.Column("model_name", sa.String(length=64), server_default="template-v1", nullable=False),
        sa.Column("model_version", sa.String(length=32), server_default="v1", nullable=False),
        sa.Column("prompt_context_hash", sa.String(length=32), nullable=True),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tutor_interactions_student", "tutor_interactions", ["student_id"])
    op.create_index(
        "ix_tutor_interactions_student_problem",
        "tutor_interactions",
        ["student_id", "problem_id"],
    )
    op.create_index("ix_tutor_interactions_created", "tutor_interactions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_tutor_interactions_created", table_name="tutor_interactions")
    op.drop_index("ix_tutor_interactions_student_problem", table_name="tutor_interactions")
    op.drop_index("ix_tutor_interactions_student", table_name="tutor_interactions")
    op.drop_table("tutor_interactions")
