"""0004 — unique constraint on test_cases (problem_id, name)

Execution results are matched back to test cases by name; duplicates
within one problem would silently corrupt evidence attribution.

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-24
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_test_cases_problem_name",
        "test_cases",
        ["problem_id", "name"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_test_cases_problem_name", "test_cases", type_="unique")
