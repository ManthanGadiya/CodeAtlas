"""Execution domain models: every run is persisted as learning evidence."""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    # run | submit (docs/DESIGN.md §44: Run gives fast feedback, Submit grades)
    mode: Mapped[str] = mapped_column(String(16))
    # SUCCESS | COMPILE_ERROR | RUNTIME_ERROR | TIMEOUT | MEMORY_LIMIT | SYSTEM_ERROR
    status: Mapped[str] = mapped_column(String(32))
    runtime_ms: Mapped[int | None] = mapped_column(Integer)
    memory_bytes: Mapped[int | None] = mapped_column(Integer)  # NULL until measured
    exit_code: Mapped[int | None] = mapped_column(Integer)
    stdout_tail: Mapped[str | None] = mapped_column(Text)
    stderr_tail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    test_executions: Mapped[list["TestCaseExecution"]] = relationship(
        back_populates="execution", cascade="all, delete-orphan"
    )


class TestCaseExecution(Base):
    __tablename__ = "test_case_executions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("executions.id", ondelete="CASCADE"), index=True
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("test_cases.id", ondelete="CASCADE")
    )
    passed: Mapped[bool] = mapped_column(Boolean)
    actual_output: Mapped[object | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)

    execution: Mapped["Execution"] = relationship(back_populates="test_executions")
