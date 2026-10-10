"""0020 — forgetting rate per skill (ROADMAP §33, Data_Model §31, §78-79).

Adds `forgetting_rate` (λ, per-skill personalized forgetting rate in 1/days)
to `retention_states`.  Estimated from Mastery(t) history via exponential fit
on mastery snapshots.  Used for personalized half-life and early-warning
skill-fading signals (ROADMAP §33, §48, §78-79).

Revision ID: 0020
Revises: 0019
Create Date: 2026-09-22
"""

import sqlalchemy as sa
from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "retention_states",
        sa.Column(
            "forgetting_rate",
            sa.Float(),
            nullable=True,
            comment="Personalized forgetting rate λ (1/days). Estimated from Mastery(t) history via exponential fit.",
        ),
    )
    op.add_column(
        "retention_states",
        sa.Column(
            "forgetting_rate_updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When forgetting_rate was last updated from Mastery(t) fit.",
        ),
    )
    op.create_index(
        "ix_retention_states_forgetting_rate", "retention_states", ["forgetting_rate"]
    )


def downgrade() -> None:
    op.drop_index("ix_retention_states_forgetting_rate", table_name="retention_states")
    op.drop_column("retention_states", "forgetting_rate_updated_at")
    op.drop_column("retention_states", "forgetting_rate")