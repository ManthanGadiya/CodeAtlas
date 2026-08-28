"""0010 — session entity and session_id scoping

Creates the Session entity per docs/Data_Model.md §9 and adds nullable
session_id FKs to the tables that are scoped to a learning session
(events, code artifacts, executions, behavior observations). Rows made
before this migration keep session_id = NULL (backfill is not required;
new rows populate it via get_or_create_open_session).

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-28
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column(
            "session_type",
            sa.String(length=32),
            server_default=sa.text("'practice'"),
            nullable=False,
        ),
        sa.Column(
            "device_context",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_student_started", "sessions", ["student_id", "started_at"])
    op.create_index("ix_sessions_student_open", "sessions", ["student_id", "ended_at"])
    op.create_index("ix_sessions_student_id", "sessions", ["student_id"])

    op.add_column("learning_events", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.create_index("ix_learning_events_session_id", "learning_events", ["session_id"])
    op.create_foreign_key(
        "fk_learning_events_session_id",
        "learning_events",
        "sessions",
        ["session_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("code_artifacts", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.create_index("ix_code_artifacts_session_id", "code_artifacts", ["session_id"])
    op.create_foreign_key(
        "fk_code_artifacts_session_id",
        "code_artifacts",
        "sessions",
        ["session_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("executions", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.create_index("ix_executions_session_id", "executions", ["session_id"])
    op.create_foreign_key(
        "fk_executions_session_id",
        "executions",
        "sessions",
        ["session_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("behavior_observations", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.create_index("ix_behavior_observations_session_id", "behavior_observations", ["session_id"])
    op.create_foreign_key(
        "fk_behavior_observations_session_id",
        "behavior_observations",
        "sessions",
        ["session_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_behavior_observations_session_id", "behavior_observations", type_="foreignkey"
    )
    op.drop_index("ix_behavior_observations_session_id", table_name="behavior_observations")
    op.drop_column("behavior_observations", "session_id")

    op.drop_constraint("fk_executions_session_id", "executions", type_="foreignkey")
    op.drop_index("ix_executions_session_id", table_name="executions")
    op.drop_column("executions", "session_id")

    op.drop_constraint("fk_code_artifacts_session_id", "code_artifacts", type_="foreignkey")
    op.drop_index("ix_code_artifacts_session_id", table_name="code_artifacts")
    op.drop_column("code_artifacts", "session_id")

    op.drop_constraint("fk_learning_events_session_id", "learning_events", type_="foreignkey")
    op.drop_index("ix_learning_events_session_id", table_name="learning_events")
    op.drop_column("learning_events", "session_id")

    op.drop_index("ix_sessions_student_id", table_name="sessions")
    op.drop_index("ix_sessions_student_open", table_name="sessions")
    op.drop_index("ix_sessions_student_started", table_name="sessions")
    op.drop_table("sessions")
