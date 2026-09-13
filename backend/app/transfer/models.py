"""Transfer evaluation persistence (Problem_Generator §49-51, Data_Model §48)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TransferEvaluation(Base):
    """One transfer probe: same skill, new surface (T1-T5)."""

    __tablename__ = "transfer_evaluations"
    __table_args__ = (
        Index("ix_transfer_student", "student_id"),
        Index("ix_transfer_skill", "skill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    source_problem_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="SET NULL"), nullable=True
    )
    transfer_problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE")
    )
    transfer_level: Mapped[str] = mapped_column(String(8), default="T2")  # T0..T5 per §50
    result: Mapped[str | None] = mapped_column(String(16), nullable=True)  # success|failure|partial
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(32), default="transfer-rule-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
