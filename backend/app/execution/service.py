"""Execution application service: orchestrates runner, persistence, response."""

from sqlalchemy.orm import Session

from app.execution.models import Execution, TestCaseExecution
from app.execution.runner import RESULTS_SENTINEL, RunOutcome
from app.problems.models import Problem, TestCase


def select_test_cases(problem: Problem, mode: str) -> list[TestCase]:
    """Run grades against visible examples only; Submit uses every case."""
    ordered = sorted(problem.test_cases, key=lambda case: case.order_index)
    if mode == "run":
        return [case for case in ordered if case.visibility == "visible"]
    return ordered


def persist_execution(
    db: Session,
    *,
    student_id,
    problem: Problem,
    mode: str,
    outcome: RunOutcome,
    executed_cases: list[TestCase],
) -> Execution:
    execution = Execution(
        student_id=student_id,
        problem_id=problem.id,
        mode=mode,
        status=outcome.status,
        runtime_ms=outcome.runtime_ms,
        memory_bytes=None,  # container memory accounting arrives later
        exit_code=outcome.exit_code,
        stdout_tail=outcome.stdout_tail[-4000:] if outcome.stdout_tail else None,
        stderr_tail=outcome.stderr_tail[-4000:] if outcome.stderr_tail else None,
    )

    results_by_name = {result["name"]: result for result in outcome.results}
    for case in executed_cases:
        result = results_by_name.get(case.name)
        if result is None:
            continue  # load error or timeout: no per-case data exists
        execution.test_executions.append(
            TestCaseExecution(
                test_case_id=case.id,
                passed=bool(result.get("passed")),
                actual_output=result.get("actual"),
                error=result.get("error"),
            )
        )

    db.add(execution)
    db.commit()
    return execution


def build_response(*, mode: str, outcome: RunOutcome, executed_cases: list[TestCase]) -> dict:
    """Shape the API payload.

    Hidden-case policy (documented in STATUS.md): hidden test cases and
    their expected outputs never leave the server. A failed submit reports
    an anonymous "hidden case" pass/fail plus the student's own error
    message — enough to know they missed an edge, not enough to hardcode.
    """
    by_name = {result["name"]: result for result in outcome.results}

    results: list[dict] = []
    hidden_failures = 0

    if outcome.load_error is None:
        for case in executed_cases:
            if case.name not in by_name:
                continue
            result = by_name[case.name]
            if case.visibility == "visible":
                results.append(
                    {
                        "name": case.name,
                        "visibility": "visible",
                        "passed": bool(result.get("passed")),
                        "actual_output": result.get("actual"),
                        "expected_output": case.expected_output,
                        "error": result.get("error"),
                    }
                )
            else:
                passed = bool(result.get("passed"))
                if not passed:
                    hidden_failures += 1
                results.append(
                    {
                        "visibility": "hidden",
                        "passed": passed,
                        "error": None if passed else result.get("error"),
                    }
                )

    passed = sum(1 for result in results if result["passed"])
    total = len(results) + hidden_failures
    message = ""
    if outcome.load_error is not None:
        message = outcome.load_error.get("message", "")
    elif hidden_failures:
        message = (
            f"{hidden_failures} hidden case(s) failed. They check generalisation "
            "beyond the visible examples — think about edge cases you haven't tried."
        )

    return {
        "status": outcome.status,
        "mode": mode,
        "runtime_ms": outcome.runtime_ms,
        "summary": {"passed": passed, "total": total},
        "results": results,
        "stdout_tail": (outcome.stdout_tail or "").split(RESULTS_SENTINEL)[0][-2000:],
        "stderr_tail": outcome.stderr_tail or "",
        "message": message,
    }
