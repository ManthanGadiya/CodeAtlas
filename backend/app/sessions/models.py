"""Session model (docs/Data_Model.md §9).

A session is a continuous learning interaction. Events, code artifacts,
executions, and behavior observations are scoped to the session that
produced them so the system can answer: what did the student do *in this
session*, how did their behavior change across sessions, and when did
they practice last (retention, behavior baselines).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

SESSION_TYPES = {
    "practice",
    "debugging",
    "diagnostic",
    "revision",
    "retrieval",
    "free_coding",
}


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_student_started", "student_id", "started_at"),
        Index("ix_sessions_student_open", "student_id", "ended_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    # practice | debugging | diagnostic | revision | retrieval | free_coding
    session_type: Mapped[str] = mapped_column(
        String(32), default="practice", server_default="practice"
    )
    device_context: Mapped[dict] = mapped_column(JSON, default=dict, server_default="{}")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
