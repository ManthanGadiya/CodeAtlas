"""0014 — retention states (ROADMAP Phase 3.6, docs/Forgetting_And_Retention.md §51).

Rule-based V1 per §56: exponential decay R(t)=exp(-t/S) with adaptive
stability (§23-24, §54).  Retention was previously a NULL placeholder on
student_skill_states; it now decays live via stability and retrieval
history.

Revision ID: 0014
Revises: 0013
Create Date: 2026-09-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "retention_states",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("stability", sa.Float(), server_default="2.5", nullable=False),
        sa.Column("retrieval_probability", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("last_successful_retrieval", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_recommended_review", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieval_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("successful_retrievals", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "model_version",
            sa.String(length=32),
            server_default="retention-rule-v1",
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "skill_id"),
    )
    op.create_index("ix_retention_states_student", "retention_states", ["student_id"])
    op.create_index(
        "ix_retention_states_next_review", "retention_states", ["next_recommended_review"]
    )


def downgrade() -> None:
    op.drop_index("ix_retention_states_next_review", table_name="retention_states")
    op.drop_index("ix_retention_states_student", table_name="retention_states")
    op.drop_table("retention_states")
