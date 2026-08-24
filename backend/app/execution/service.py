"""Execution application service: orchestrates runner, persistence, response."""

import difflib
import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.events.service import record_event
from app.execution.models import CodeArtifact, Execution, TestCaseExecution
from app.execution.runner import RESULTS_SENTINEL, RunOutcome
from app.problems.models import Problem, TestCase


def record_artifact(db: Session, *, student_id, problem: Problem, code: str) -> CodeArtifact:
    """Store this submission as the newest version in the problem's chain.

    Consecutive identical submissions are deduplicated by content hash;
    otherwise the artifact links to the previous version with a unified
    diff (docs/Data_Model.md §14-16).
    """
    content_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
    latest = db.scalar(
        select(CodeArtifact)
        .where(
            CodeArtifact.student_id == student_id,
            CodeArtifact.problem_id == problem.id,
        )
        .order_by(CodeArtifact.created_at.desc())
        .limit(1)
    )

    if latest is not None and latest.content_hash == content_hash:
        return latest

    diff_text = None
    if latest is not None:
        diff_text = "\n".join(
            difflib.unified_diff(
                latest.source_code.splitlines(),
                code.splitlines(),
                fromfile=f"v-{latest.id.hex[:8]}",
                tofile="submission",
                lineterm="",
            )
        )

    artifact = CodeArtifact(
        student_id=student_id,
        problem_id=problem.id,
        source_code=code,
        content_hash=content_hash,
        parent_artifact_id=latest.id if latest is not None else None,
        diff_text=diff_text,
    )
    db.add(artifact)
    db.commit()
    return artifact


def emit_execution_events(
    db: Session,
    *,
    student_id,
    problem: Problem,
    mode: str,
    outcome: RunOutcome,
    executed_cases: list[TestCase],
) -> None:
    """Record the learning-event trail for one execution (Phase 1.4).

    Faithful to docs/Data_Model.md §11: CODE_RUN summarises the attempt;
    failure statuses get their documented distinct events; Submit-mode
    grading additionally records per-case TEST_PASSED / TEST_FAILED.
    Events are internal evidence — hidden case names may appear here even
    though they never reach API responses.
    """
    passed = sum(1 for result in outcome.results if result.get("passed"))
    total = len(outcome.results)
    record_event(
        db,
        student_id=student_id,
        event_type="CODE_RUN",
        payload={
            "problem_slug": problem.slug,
            "mode": mode,
            "status": outcome.status,
            "passed": passed,
            "total": total,
        },
    )

    if outcome.status == "COMPILE_ERROR":
        record_event(
            db,
            student_id=student_id,
            event_type="COMPILATION_FAILED",
            payload={"problem_slug": problem.slug, "mode": mode},
        )
    elif outcome.status == "RUNTIME_ERROR":
        record_event(
            db,
            student_id=student_id,
            event_type="RUNTIME_FAILED",
            payload={"problem_slug": problem.slug, "mode": mode},
        )

    if mode != "submit" or outcome.load_error is not None or outcome.status != "SUCCESS":
        return

    visibility_by_name = {case.name: case.visibility for case in executed_cases}
    for case_result in outcome.results:
        record_event(
            db,
            student_id=student_id,
            event_type=("TEST_PASSED" if case_result.get("passed") else "TEST_FAILED"),
            payload={
                "problem_slug": problem.slug,
                "case_name": case_result["name"],
                "visibility": visibility_by_name.get(case_result["name"], "hidden"),
                "error": case_result.get("error"),
            },
        )

    if total > 0 and passed == total:
        record_event(
            db,
            student_id=student_id,
            event_type="PROBLEM_COMPLETED",
            payload={"problem_slug": problem.slug},
        )


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
    artifact: CodeArtifact | None = None,
) -> Execution:
    execution = Execution(
        student_id=student_id,
        problem_id=problem.id,
        code_artifact_id=artifact.id if artifact is not None else None,
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
