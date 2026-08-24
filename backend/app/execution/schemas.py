"""Pydantic schemas for code execution requests and responses."""

from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100_000)


class TestCaseResult(BaseModel):
    """Visible cases carry full detail; hidden cases are anonymous pass/fail."""

    name: str | None = None
    visibility: str
    passed: bool
    actual_output: object | None = None
    expected_output: object | None = None
    error: str | None = None


class ExecutionResponse(BaseModel):
    status: str
    mode: str
    runtime_ms: int | None
    summary: dict  # {"passed": int, "total": int}
    results: list[TestCaseResult]
    stdout_tail: str = ""
    stderr_tail: str = ""
    message: str = ""  # load-error detail (compile/runtime), empty otherwise
