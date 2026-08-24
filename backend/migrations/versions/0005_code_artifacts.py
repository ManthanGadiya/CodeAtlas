"""0005 — code_artifacts and executions.code_artifact_id

Code version history per docs/ROADMAP.md Phase 1.5 and docs/Data_Model.md
§14-16: a parent-linked chain of student code versions with content hashes
and unified diffs.

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-24
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "code_artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("problem_id", sa.Uuid(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False, server_default="python"),
        sa.Column("source_code", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("parent_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("diff_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_artifact_id"], ["code_artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_code_artifacts_student_problem",
        "code_artifacts",
        ["student_id", "problem_id"],
    )

    op.add_column(
        "executions",
        sa.Column("code_artifact_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_executions_code_artifact_id",
        "executions",
        "code_artifacts",
        ["code_artifact_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_executions_code_artifact_id"), "executions", ["code_artifact_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_executions_code_artifact_id"), table_name="executions")
    op.drop_constraint("fk_executions_code_artifact_id", "executions", type_="foreignkey")
    op.drop_column("executions", "code_artifact_id")
    op.drop_index("ix_code_artifacts_student_problem", table_name="code_artifacts")
    op.drop_table("code_artifacts")
