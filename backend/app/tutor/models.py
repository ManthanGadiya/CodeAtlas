"""Tutor interaction persistence (docs/Data_Model.md §43).

Every tutor response is auditable: provider, model, latency, context hash,
and the hint level that produced it.  The table stays append-only — a
correction is a new row, never an edit (same principle as learning_events).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TutorInteraction(Base):
    """One tutor response for one student session.

    ``hint_level`` follows the 0-7 ladder from docs/Tutoring_Engine.md §7-8
    and ROADMAP §22: 0 = no help, 1 = directional question, ... 7 = full
    solution. ``interaction_type`` mirrors the mode list in §5 (SOCRACTIC,
    HINT, EXPLANATION, ...).  ``model_version`` records the Prompt/Gateway
    version so later evaluation can compare interventions.
    """

    __tablename__ = "tutor_interactions"
    __table_args__ = (
        Index("ix_tutor_interactions_student", "student_id"),
        Index("ix_tutor_interactions_student_problem", "student_id", "problem_id"),
        Index("ix_tutor_interactions_created", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True
    )
    problem_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), nullable=True
    )
    # SOCRATIC | HINT | DEBUGGING | CONCEPT | REVIEW | ... (Tutoring_Engine.md §5)
    interaction_type: Mapped[str] = mapped_column(String(24), default="HINT")
    # 0..7 inclusive; 0 = observe silently (DESIGN.md §34)
    hint_level: Mapped[int] = mapped_column(Integer, default=1)
    # Human-readable intervention label chosen by the engine (e.g. "SOCRATIC_QUESTION")
    intervention: Mapped[str] = mapped_column(String(32), default="HINT")
    # AI gateway bookkeeping — dummy provider uses "template-v1"
    model_provider: Mapped[str] = mapped_column(String(32), default="dummy")
    model_name: Mapped[str] = mapped_column(String(64), default="template-v1")
    model_version: Mapped[str] = mapped_column(String(32), default="v1")
    prompt_context_hash: Mapped[str | None] = mapped_column(String(32))
    response: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
