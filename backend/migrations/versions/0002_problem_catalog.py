"""0002 — skills, problems, problem_skills, test_cases

Problem catalog tables per docs/Data_Model.md §86 (Version 1 core set).
Hand-written to match app/problems/models.py exactly.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-24
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("parent_skill_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["parent_skill_id"], ["skills.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skills_slug"), "skills", ["slug"], unique=True)

    op.create_table(
        "problems",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=16), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False, server_default="python"),
        sa.Column("source_type", sa.String(length=16), nullable=False, server_default="curated"),
        sa.Column("starter_code", sa.Text(), nullable=False, server_default=""),
        sa.Column("function_name", sa.String(length=120), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_problems_slug"), "problems", ["slug"], unique=True)

    op.create_table(
        "problem_skills",
        sa.Column("problem_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="primary"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("problem_id", "skill_id"),
    )
    op.create_index(op.f("ix_problem_skills_skill_id"), "problem_skills", ["skill_id"])

    op.create_table(
        "test_cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("problem_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("input_args", sa.JSON(), nullable=False),
        sa.Column("expected_output", sa.JSON(), nullable=False),
        sa.Column("visibility", sa.String(length=16), nullable=False, server_default="hidden"),
        sa.Column("test_type", sa.String(length=16), nullable=False, server_default="normal"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_cases_problem_id"), "test_cases", ["problem_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_test_cases_problem_id"), table_name="test_cases")
    op.drop_table("test_cases")
    op.drop_table("problem_skills")
    op.drop_index(op.f("ix_problems_slug"), table_name="problems")
    op.drop_table("problems")
    op.drop_index(op.f("ix_skills_slug"), table_name="skills")
    op.drop_table("skills")
