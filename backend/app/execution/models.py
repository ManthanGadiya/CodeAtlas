"""Execution domain models: every run is persisted as learning evidence."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CodeArtifact(Base):
    """A meaningful version of student code (docs/Data_Model.md §14-16).

    Versions form a parent chain; each artifact stores a unified diff
    against its parent so debugging behaviour can be studied later.
    Identical consecutive submissions are deduplicated by content hash.
    """

    __tablename__ = "code_artifacts"
    __table_args__ = (Index("ix_code_artifacts_student_problem", "student_id", "problem_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE")
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE")
    )
    language: Mapped[str] = mapped_column(String(32), default="python", server_default="python")
    source_code: Mapped[str] = mapped_column(Text)
    # SHA-256 hex digest of source_code: deduplication + integrity (§70).
    content_hash: Mapped[str] = mapped_column(String(64))
    parent_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("code_artifacts.id", ondelete="SET NULL")
    )
    diff_text: Mapped[str | None] = mapped_column(Text)
    # Python-side default: microsecond precision, because "latest artifact"
    # ordering must be stable even for submissions within the same second
    # (SQLite's CURRENT_TIMESTAMP only has second granularity).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    code_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("code_artifacts.id", ondelete="SET NULL"), index=True
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
