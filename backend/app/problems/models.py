"""Problem domain models: skills, problems, mappings, and test cases.

These correspond to the Version-1 core tables in docs/Data_Model.md §86
(problems, skills, problem_skills, test_cases). Test cases are stored here
already even though execution arrives in Phase 1.3 — a fully specified
problem includes its evaluation strategy.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    parent_skill_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("skills.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Self-referential hierarchy (docs/System_Architecture.md §14); depth stays shallow for V1.
    parent: Mapped["Skill | None"] = relationship(remote_side=[id])


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    # Coarse label for V1; multidimensional difficulty vector arrives later
    # (docs/Problem_Generator.md §14).
    difficulty: Mapped[str] = mapped_column(String(16))  # easy | medium | hard
    language: Mapped[str] = mapped_column(String(32), default="python", server_default="python")
    source_type: Mapped[str] = mapped_column(
        String(16), default="curated", server_default="curated"
    )
    starter_code: Mapped[str] = mapped_column(Text, default="", server_default="")
    # Function-call evaluation contract: the sandbox will invoke
    # function_name(*test_case.input_args) and compare against expected_output.
    function_name: Mapped[str] = mapped_column(String(120))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    skill_links: Mapped[list["ProblemSkill"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan"
    )
    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan", order_by="TestCase.order_index"
    )


class ProblemSkill(Base):
    __tablename__ = "problem_skills"

    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True
    )
    # Standalone index serves the future skill->problems recommendation path.
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    # primary | supporting (docs/Data_Model.md §28)
    role: Mapped[str] = mapped_column(String(16), default="primary", server_default="primary")

    problem: Mapped["Problem"] = relationship(back_populates="skill_links")
    skill: Mapped["Skill"] = relationship()


class TestCase(Base):
    __tablename__ = "test_cases"
    # Execution results are matched back to cases by name; duplicates within
    # one problem would silently corrupt evidence attribution.
    __table_args__ = (UniqueConstraint("problem_id", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    problem_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    input_args: Mapped[list] = mapped_column(JSON)
    expected_output: Mapped[object] = mapped_column(JSON)
    # Hidden tests evaluate generalisation (docs/Problem_Generator.md §57-58):
    # they never appear in API payloads — grading surfaces only an anonymous
    # pass/fail for them.
    visibility: Mapped[str] = mapped_column(
        String(16), default="hidden", server_default="hidden"
    )  # visible | hidden
    test_type: Mapped[str] = mapped_column(
        String(16), default="normal", server_default="normal"
    )  # normal | edge | boundary
    order_index: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    problem: Mapped["Problem"] = relationship(back_populates="test_cases")
