"""0012 — aggregate student state + remaining Level 2 columns

Closes the last Data_Model gaps flagged as High/Medium: per-student
aggregate rollup (StudentLearningState) and preferences table, plus the
two columns that snapshots/observations should have carried from the
start (mastery_snapshots.confidence, behavior_observations.confidence).

Revision ID: 0012
Revises: 0011
Create Date: 2026-09-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_preferences",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column(
            "preferred_language", sa.String(length=32), server_default="python", nullable=False
        ),
        sa.Column("preferred_difficulty", sa.String(length=16), nullable=True),
        sa.Column("explanation_style", sa.String(length=32), nullable=True),
        sa.Column("hint_style", sa.String(length=32), nullable=True),
        sa.Column("session_length", sa.Integer(), nullable=True),
        sa.Column("notification_preferences", sa.JSON(), server_default="{}", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id"),
    )

    op.create_table(
        "student_learning_states",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("overall_mastery", sa.Float(), server_default="0.3", nullable=False),
        sa.Column("learning_velocity", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("independence_score", sa.Float(), server_default="0.5", nullable=False),
        sa.Column("retention_score", sa.Float(), server_default="0.5", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id"),
    )

    op.add_column("mastery_snapshots", sa.Column("confidence", sa.Float(), nullable=True))
    op.add_column(
        "behavior_observations",
        sa.Column("confidence", sa.Float(), server_default="0.5", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("behavior_observations", "confidence")
    op.drop_column("mastery_snapshots", "confidence")
    op.drop_table("student_learning_states")
    op.drop_table("student_preferences")
