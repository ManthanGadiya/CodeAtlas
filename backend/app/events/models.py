"""Learning-event model — the historical truth of CodeAtlas.

Events are immutable append-only records (docs/Data_Model.md §13): a
correction is a new event, never an edit. The learner model will later be
derived from this stream, so event semantics are deliberately stable
(AGENTS.md §32-33): every event carries a schema_version for future
migrations.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LearningEvent(Base):
    __tablename__ = "learning_events"
    __table_args__ = (Index("ix_learning_events_student_type", "student_id", "event_type"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE")
    )
    # Nullable until Session exists (pre-0010 rows) and for future
    # system events that are not session-scoped.
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Controlled vocabulary in app/events/service.py EVENT_TYPES; extended
    # only deliberately, never casually (AGENTS.md §32).
    event_type: Mapped[str] = mapped_column(String(48))
    schema_version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    # Microsecond Python-side default: event timestamps are the ordering
    # key for analysis (docs/Data_Model.md §78-79) and SQLite's
    # CURRENT_TIMESTAMP only has second granularity.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
