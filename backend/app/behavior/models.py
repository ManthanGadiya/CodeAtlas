"""Behavior domain models (docs/Data_Model.md §38-40).

Observations are threshold crossings recorded when they happen; patterns
aggregate them per (student, behavior_type). Both are derived data —
every row names the rule version that produced it (docs/Data_Model.md §47).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BehaviorObservation(Base):
    """One fired behavioral signal on one execution."""

    __tablename__ = "behavior_observations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    behavior_type: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(16))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    model_version: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )


class BehaviorPattern(Base):
    """Aggregated signal per (student, behavior_type) (docs/Data_Model.md §40)."""

    __tablename__ = "behavior_patterns"

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    behavior_type: Mapped[str] = mapped_column(String(32), primary_key=True)
    frequency: Mapped[int] = mapped_column(Integer, default=0)
    severity: Mapped[str] = mapped_column(String(16))
    # Derived later from recent-vs-total frequency; honest placeholder now.
    trend: Mapped[str] = mapped_column(String(16), default="UNKNOWN", server_default="UNKNOWN")
    confidence: Mapped[float] = mapped_column(Float, default=0.3)
    last_observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
