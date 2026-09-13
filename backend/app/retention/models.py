"""Retention state persistence (docs/Data_Model.md §49, Forgetting §51).

Each row tracks one (student, skill) memory trace: its stability
(resistance to forgetting, in days), retrieval probability, and the
next recommended review.  This is the forgetting half that the mastery
engine deliberately left NULL (skills/models.py).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RetentionState(Base):
    """Per-skill memory stability and scheduling (one row per learner skill).

    ``stability`` follows docs/Forgetting_And_Retention.md §23: days a
    skill survives before retention drops to ~0.37 (1/e).  It grows on
    successful delayed retrieval (§24) and shrinks on failure (§54).
    ``retrieval_probability`` is the current R(t) = exp(-t/S) estimate.
    ``next_recommended_review`` is stability-scaled scheduling (§22).
    """

    __tablename__ = "retention_states"

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    # Resistance to forgetting, in days.  Initial ~2.5 days mirrors §54 example.
    stability: Mapped[float] = mapped_column(Float, default=2.5)
    # Last point at which R(t) was evaluated (for reproducibility)
    retrieval_probability: Mapped[float] = mapped_column(Float, default=1.0)
    last_successful_retrieval: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_recommended_review: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retrieval_count: Mapped[int] = mapped_column(default=0)
    successful_retrievals: Mapped[int] = mapped_column(default=0)
    # Model version for reproducibility (Data_Model §47, Forgetting §56)
    model_version: Mapped[str] = mapped_column(String(32), default="retention-rule-v1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
