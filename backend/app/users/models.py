"""Student ORM model — the identity and profile root of the data model."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(100))
    timezone: Mapped[str | None] = mapped_column(String(64))
    preferred_language: Mapped[str] = mapped_column(
        String(32), default="python", server_default="python"
    )
    status: Mapped[str] = mapped_column(String(16), default="active", server_default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StudentPreferences(Base):
    """Learning preferences separate from ability (docs/Data_Model.md §7)."""

    __tablename__ = "student_preferences"

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    preferred_language: Mapped[str] = mapped_column(
        String(32), default="python", server_default="python"
    )
    preferred_difficulty: Mapped[str | None] = mapped_column(String(16))
    explanation_style: Mapped[str | None] = mapped_column(String(32))
    hint_style: Mapped[str | None] = mapped_column(String(32))
    session_length: Mapped[int | None] = mapped_column(Integer)
    notification_preferences: Mapped[dict] = mapped_column(JSON, default=dict, server_default="{}")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StudentLearningState(Base):
    """Aggregate derived state per student (docs/Data_Model.md §8)."""

    __tablename__ = "student_learning_states"

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    overall_mastery: Mapped[float] = mapped_column(Float, default=0.3, server_default="0.3")
    learning_velocity: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0")
    independence_score: Mapped[float] = mapped_column(Float, default=0.5, server_default="0.5")
    retention_score: Mapped[float] = mapped_column(Float, default=0.5, server_default="0.5")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
