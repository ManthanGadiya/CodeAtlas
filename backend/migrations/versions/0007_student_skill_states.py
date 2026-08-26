"""0007 — student skill states and mastery snapshots

Learner-model knowledge half per docs/Data_Model.md §29-31 and
docs/ROADMAP.md Phase 2.4: the current mastery belief per (student,
skill) pair plus an append-only snapshot trail that keeps every change
explainable and replayable (docs/Learning_Model.md rules 6, 7, 12).

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-26
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_skill_states",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("mastery", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("retention", sa.Float(), nullable=True),
        sa.Column("evidence_count", sa.Integer(), nullable=False),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "skill_id"),
    )
    op.create_index("ix_student_skill_states_skill_id", "student_skill_states", ["skill_id"])

    op.create_table(
        "mastery_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("previous_mastery", sa.Float(), nullable=True),
        sa.Column("new_mastery", sa.Float(), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mastery_snapshots_student_id", "mastery_snapshots", ["student_id"])
    op.create_index("ix_mastery_snapshots_skill_id", "mastery_snapshots", ["skill_id"])
    op.create_index(
        "ix_mastery_snapshots_student_skill_time",
        "mastery_snapshots",
        ["student_id", "skill_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mastery_snapshots_student_skill_time", table_name="mastery_snapshots"
    )
    op.drop_index("ix_mastery_snapshots_skill_id", table_name="mastery_snapshots")
    op.drop_index("ix_mastery_snapshots_student_id", table_name="mastery_snapshots")
    op.drop_table("mastery_snapshots")
    op.drop_index("ix_student_skill_states_skill_id", table_name="student_skill_states")
    op.drop_table("student_skill_states")
