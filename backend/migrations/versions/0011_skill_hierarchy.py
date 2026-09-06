"""0011 — skill hierarchy completeness

Adds the columns that Data_Model.md §25-28 document but Phase 1.2
deferred, and creates the prerequisite graph table so Level 2 can
reason about root causes (Learning_Model.md §14-15).

Revision ID: 0011
Revises: 0010
Create Date: 2026-08-28
"""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("skills", sa.Column("domain", sa.String(length=64), nullable=True))

    op.add_column(
        "problem_skills",
        sa.Column(
            "importance",
            sa.Float(),
            nullable=False,
            server_default="1.0",
        ),
    )

    op.create_table(
        "skill_relationships",
        sa.Column("source_skill_id", sa.Uuid(), nullable=False),
        sa.Column("target_skill_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_type", sa.String(length=32), nullable=False),
        sa.Column("strength", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["source_skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("source_skill_id", "target_skill_id"),
        sa.UniqueConstraint("source_skill_id", "target_skill_id", name="uq_skill_relationship"),
    )
    op.create_index("ix_skill_relationships_source", "skill_relationships", ["source_skill_id"])
    op.create_index("ix_skill_relationships_target", "skill_relationships", ["target_skill_id"])


def downgrade() -> None:
    op.drop_index("ix_skill_relationships_target", table_name="skill_relationships")
    op.drop_index("ix_skill_relationships_source", table_name="skill_relationships")
    op.drop_table("skill_relationships")
    op.drop_column("problem_skills", "importance")
    op.drop_column("skills", "domain")
    op.drop_column("skills", "description")
