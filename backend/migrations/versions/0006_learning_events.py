"""0006 — learning_events

Immutable, versioned event stream per docs/Data_Model.md §10-13 and
docs/ROADMAP.md Phase 1.4. The event stream is the historical truth of
CodeAtlas; learner models are derived from it later.

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-24
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=48), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_learning_events_student_type",
        "learning_events",
        ["student_id", "event_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_learning_events_student_type", table_name="learning_events")
    op.drop_table("learning_events")
