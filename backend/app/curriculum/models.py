"""Curriculum decision persistence (docs/Data_Model.md §53-54).

Every adaptive recommendation is auditable: why this problem, why now,
what alternatives were considered.  Decisions are append-only like
mastery snapshots — a correction is a new row.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CurriculumDecision(Base):
    """One adaptive selection of a next problem for a student.

    ``decision_type`` mirrors Adaptive_Curriculum §11: REINFORCE | REPAIR |
    EXTEND | RETRIEVE | TRANSFER.  ``reason`` is human-readable and
    surfaces in the dashboard (explainable recommendation §75).
    """

    __tablename__ = "curriculum_decisions"
    __table_args__ = (
        Index("ix_curriculum_decisions_student", "student_id"),
        Index("ix_curriculum_decisions_created", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    selected_problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE")
    )
    target_skill_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True
    )
    decision_type: Mapped[str] = mapped_column(String(16))  # REINFORCE etc.
    reason: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.6)
    model_version: Mapped[str] = mapped_column(String(32), default="curriculum-rule-v1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )


class DecisionCandidate(Base):
    """One alternative considered for a decision (§54).  Explains why
    the selected problem beat the others — curriculum transparency.
    """

    __tablename__ = "decision_candidates"
    __table_args__ = (Index("ix_decision_candidates_decision", "decision_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    decision_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("curriculum_decisions.id", ondelete="CASCADE"), index=True
    )
    candidate_problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE")
    )
    score: Mapped[float] = mapped_column(Float)
    expected_learning_gain: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_success: Mapped[float | None] = mapped_column(Float, nullable=True)
    retention_value: Mapped[float | None] = mapped_column(Float, nullable=True)
