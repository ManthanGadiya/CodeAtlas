"""0015 — curriculum decisions (ROADMAP Phase 3.4, Data_Model §53-54).

Persists every adaptive recommendation (§53) and its considered alternatives
(§54) so the curriculum is auditable and explainable.

Revision ID: 0015
Revises: 0014
Create Date: 2026-09-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "curriculum_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("selected_problem_id", sa.Uuid(), nullable=False),
        sa.Column("target_skill_id", sa.Uuid(), nullable=True),
        sa.Column("decision_type", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="0.6", nullable=False),
        sa.Column(
            "model_version",
            sa.String(length=32),
            server_default="curriculum-rule-v1",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["selected_problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_skill_id"], ["skills.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_curriculum_decisions_student", "curriculum_decisions", ["student_id"])
    op.create_index("ix_curriculum_decisions_created", "curriculum_decisions", ["created_at"])

    op.create_table(
        "decision_candidates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("candidate_problem_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("expected_learning_gain", sa.Float(), nullable=True),
        sa.Column("expected_success", sa.Float(), nullable=True),
        sa.Column("retention_value", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["candidate_problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["decision_id"], ["curriculum_decisions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_decision_candidates_decision", "decision_candidates", ["decision_id"])


def downgrade() -> None:
    op.drop_index("ix_decision_candidates_decision", table_name="decision_candidates")
    op.drop_table("decision_candidates")
    op.drop_index("ix_curriculum_decisions_created", table_name="curriculum_decisions")
    op.drop_index("ix_curriculum_decisions_student", table_name="curriculum_decisions")
    op.drop_table("curriculum_decisions")
