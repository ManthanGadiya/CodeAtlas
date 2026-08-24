"""Code execution endpoints: Run (visible examples) and Submit (all tests)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import CurrentUser, DbSession
from app.core.ratelimit import execution_limiter
from app.execution import schemas
from app.execution import service as execution_service
from app.execution.runner import DockerPythonRunner, RunnerUnavailableError, get_runner
from app.problems import service as problem_service

router = APIRouter(prefix="/problems", tags=["execution"])

Runner = Annotated[DockerPythonRunner, Depends(get_runner)]


def _execution_budget(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not execution_limiter.allow(f"exec:{client_ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many executions in a minute. Take a moment to think it through.",
        )


def _execute(
    slug: str,
    mode: str,
    payload: schemas.ExecuteRequest,
    db: DbSession,
    student: CurrentUser,
    runner: Runner,
) -> schemas.ExecutionResponse:
    problem = problem_service.get_problem_by_slug(db, slug)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    executed_cases = execution_service.select_test_cases(problem, mode)
    try:
        outcome = runner.run(
            code=payload.code,
            function_name=problem.function_name,
            tests=[
                {
                    "name": case.name,
                    "input_args": case.input_args,
                    "expected_output": case.expected_output,
                }
                for case in executed_cases
            ],
        )
    except RunnerUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{exc} Start your Docker engine and try again.",
        ) from exc

    execution_service.persist_execution(
        db,
        student_id=student.id,
        problem=problem,
        mode=mode,
        outcome=outcome,
        executed_cases=executed_cases,
    )

    response = execution_service.build_response(
        mode=mode,
        outcome=outcome,
        executed_cases=executed_cases,
    )
    return schemas.ExecutionResponse(**response)


@router.post("/{slug}/run", response_model=schemas.ExecutionResponse)
def run_code(
    slug: str,
    payload: schemas.ExecuteRequest,
    request: Request,
    db: DbSession,
    student: CurrentUser,
    runner: Runner,
) -> schemas.ExecutionResponse:
    _execution_budget(request)
    return _execute(slug, "run", payload, db, student, runner)


@router.post("/{slug}/submit", response_model=schemas.ExecutionResponse)
def submit_code(
    slug: str,
    payload: schemas.ExecuteRequest,
    request: Request,
    db: DbSession,
    student: CurrentUser,
    runner: Runner,
) -> schemas.ExecutionResponse:
    _execution_budget(request)
    return _execute(slug, "submit", payload, db, student, runner)
