"""Retrieval schedule persistence (Forgetting_And_Retention §51-52, Data_Model §48-49)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RetrievalSchedule(Base):
    """One deliberate retrieval due for a student/skill (§20-22, §51)."""

    __tablename__ = "retrieval_schedules"
    __table_args__ = (
        Index("ix_retrieval_schedules_student", "student_id"),
        Index("ix_retrieval_schedules_due", "scheduled_for"),
        Index("ix_retrieval_schedules_skill", "skill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    problem_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="SET NULL"), nullable=True
    )
    ladder_level: Mapped[str] = mapped_column(
        String(24), default="recall"
    )  # recognition|explain|partial|recall|application|transfer
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending|completed|skipped
    result: Mapped[str | None] = mapped_column(String(16), nullable=True)  # success|failure|partial
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_taken_ms: Mapped[int | None] = mapped_column(nullable=True)
    model_version: Mapped[str] = mapped_column(String(32), default="retrieval-rule-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
