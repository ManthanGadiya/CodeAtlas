"""0008 — mistake detection tables

Mistake categories (reference taxonomy), mistakes, and recurrence
patterns per docs/Data_Model.md §34-37 and docs/ROADMAP.md Phase 2.2.
The category rows are seeded from the canonical M01-M24 list in
docs/Mistake_Taxonomy.md §5 via the shared app.mistakes.taxonomy source.

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-26
"""

import sqlalchemy as sa
from alembic import op

from app.mistakes.taxonomy import TAXONOMY_V1, category_id

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mistake_categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["mistake_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mistake_categories_code", "mistake_categories", ["code"], unique=True)

    op.create_table(
        "mistakes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("problem_id", sa.Uuid(), nullable=False),
        sa.Column("execution_id", sa.Uuid(), nullable=True),
        sa.Column("code_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_note", sa.Text(), nullable=True),
        sa.Column(
            "resolution_status",
            sa.String(length=16),
            server_default="UNRESOLVED",
            nullable=False,
        ),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["execution_id"], ["executions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["code_artifact_id"], ["code_artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["category_id"], ["mistake_categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mistakes_student_id", "mistakes", ["student_id"])
    op.create_index("ix_mistakes_problem_id", "mistakes", ["problem_id"])
    op.create_index("ix_mistakes_student_category", "mistakes", ["student_id", "category_id"])

    op.create_table(
        "mistake_patterns",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("occurrence_count", sa.Integer(), nullable=False),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["mistake_categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "category_id", "skill_id"),
    )

    category_table = sa.table(
        "mistake_categories",
        sa.column("id", sa.Uuid),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("parent_id", sa.Uuid),
    )
    op.bulk_insert(
        category_table,
        [
            {
                "id": category_id(code),
                "code": code,
                "name": name,
                "description": None,
                "parent_id": None,
            }
            for code, name in TAXONOMY_V1
        ],
    )


def downgrade() -> None:
    op.drop_table("mistake_patterns")
    op.drop_index("ix_mistakes_student_category", table_name="mistakes")
    op.drop_index("ix_mistakes_problem_id", table_name="mistakes")
    op.drop_index("ix_mistakes_student_id", table_name="mistakes")
    op.drop_table("mistakes")
    op.drop_index("ix_mistake_categories_code", table_name="mistake_categories")
    op.drop_table("mistake_categories")
