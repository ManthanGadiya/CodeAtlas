"""Student skill-state models (docs/Data_Model.md §29-31).

The learner model's knowledge half: current mastery belief per skill plus
an immutable snapshot trail so any mastery value can be explained by
replaying its update history (docs/Learning_Model.md rules 6, 7, 12).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StudentSkillState(Base):
    """Current mastery belief for one (student, skill) pair.

    Belief, not truth: ``mastery`` is a [0,1] estimate of P(student applies
    the skill), clamped by the update engine to [0.02, 0.98] so every state
    stays revisable. ``retention`` is modelled separately from mastery
    (docs/Learning_Model.md rule 4) and stays NULL until the retention
    engine estimates it — missing evidence is never weakness.
    """

    __tablename__ = "student_skill_states"

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    # Standalone index serves the future skill->students recommendation path.
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    mastery: Mapped[float] = mapped_column(Float, default=0.3)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    retention: Mapped[float | None] = mapped_column(Float)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # Version of the mastery engine that produced these numbers
    # (docs/Data_Model.md §30 — every derived value names its model).
    model_version: Mapped[str] = mapped_column(String(32))


class MasterySnapshot(Base):
    """Append-only audit trail of mastery changes (docs/Data_Model.md §31).

    A decrease is a valid snapshot. Replaying the snapshot sequence for a
    (student, skill) pair must reproduce the current state value.
    """

    __tablename__ = "mastery_snapshots"
    __table_args__ = (
        Index("ix_mastery_snapshots_student_skill_time", "student_id", "skill_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("skills.id", ondelete="CASCADE"), index=True
    )
    previous_mastery: Mapped[float | None] = mapped_column(Float)  # NULL = first evidence
    new_mastery: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String(120))
    model_version: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
