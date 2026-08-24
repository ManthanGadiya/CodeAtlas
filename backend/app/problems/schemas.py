"""Pydantic schemas for the problem catalog."""

from pydantic import BaseModel, ConfigDict


class ProblemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    difficulty: str
    language: str
    estimated_minutes: int | None


class VisibleTestCase(BaseModel):
    """A student-visible example.

    Hidden test cases — and their expected outputs — never leave the
    server; a failed submit only reports an anonymous pass/fail for them.
    `test_type` is also omitted: revealing which examples are edge/boundary
    probes would undermine diagnostic integrity (docs/DESIGN.md §23).
    """

    name: str
    input_args: list
    expected_output: object


class ProblemDetail(ProblemSummary):
    description: str
    starter_code: str
    function_name: str
    skills: list[str]
    examples: list[VisibleTestCase]
