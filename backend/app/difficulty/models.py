"""Difficulty vector persistence (Data_Model §23-24, Problem_Generator §14-15)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProblemDifficulty(Base):
    """Multidimensional difficulty vector per problem (§14-15)."""

    __tablename__ = "problem_difficulties"

    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True
    )
    overall: Mapped[float] = mapped_column(Float)
    conceptual: Mapped[float] = mapped_column(Float)
    implementation: Mapped[float] = mapped_column(Float)
    reasoning: Mapped[float] = mapped_column(Float)
    debugging: Mapped[float] = mapped_column(Float)
    constraints: Mapped[float] = mapped_column(Float)
    transfer: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float, default=0.6)
    model_version: Mapped[str] = mapped_column(String(32), default="difficulty-rule-v1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DifficultyCalibration(Base):
    """History of difficulty adjustments (§24, §86)."""

    __tablename__ = "difficulty_calibrations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    problem_id: Mapped[uuid.UUID] = mapped_column(  # noqa: E501
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    old_overall: Mapped[float] = mapped_column(Float)
    new_overall: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String(256))
    model_version: Mapped[str] = mapped_column(String(32), default="difficulty-rule-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
