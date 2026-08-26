"""Mistake domain models (docs/Data_Model.md §34-37).

Mistakes are the bridge between raw execution outcomes and the learner
model: what went wrong, how sure we are, and whether it keeps happening.
Categories are reference rows, never arbitrary strings (§35); patterns
track recurrence per (student, category, skill) so the same failure
across different problems becomes visible (§37-38).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MistakeCategory(Base):
    """Reference taxonomy row; seeded from docs/Mistake_Taxonomy.md §5."""

    __tablename__ = "mistake_categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(8), unique=True, index=True)  # e.g. "M01"
    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("mistake_categories.id", ondelete="SET NULL")
    )


class Mistake(Base):
    """One detected mistake on one submission.

    ``execution_id``/``code_artifact_id`` use SET NULL: purging old
    executions must not erase mistake history. ``category_id`` uses
    RESTRICT: a taxonomy row backing existing mistakes is not deletable.
    """

    __tablename__ = "mistakes"
    __table_args__ = (Index("ix_mistakes_student_category", "student_id", "category_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    execution_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("executions.id", ondelete="SET NULL")
    )
    code_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("code_artifacts.id", ondelete="SET NULL")
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("mistake_categories.id", ondelete="RESTRICT")
    )
    # LOW | MEDIUM | HIGH | CRITICAL (docs/Mistake_Taxonomy.md §30)
    severity: Mapped[str] = mapped_column(String(16))
    confidence: Mapped[float] = mapped_column(Float)
    evidence_note: Mapped[str | None] = mapped_column(Text)  # MistakeEvidence §36, V1 inline
    # UNRESOLVED until a later submit for the same problem fully passes (§46)
    resolution_status: Mapped[str] = mapped_column(
        String(16), default="UNRESOLVED", server_default="UNRESOLVED"
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )


class MistakePattern(Base):
    """Recurrence counter per (student, category, skill) (docs/Data_Model.md §37).

    occurrence_count >= 2 is the system's deterministic "repeated mistake"
    signal; cross-problem recurrence falls out of the skill key naturally.
    """

    __tablename__ = "mistake_patterns"

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("mistake_categories.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.3)
