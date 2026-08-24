"""Analytics summary queries — observations only, honestly labelled."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.execution.models import Execution
from app.problems.models import Problem


def build_summary(db: Session, student_id) -> dict:
    executions = db.scalars(
        select(Execution)
        .where(Execution.student_id == student_id)
        .order_by(Execution.created_at.desc())
    ).all()

    problems_by_id = {}
    if executions:
        problem_ids = {execution.problem_id for execution in executions}
        problems_by_id = {
            problem.id: problem
            for problem in db.scalars(select(Problem).where(Problem.id.in_(problem_ids)))
        }

    runs = sum(1 for e in executions if e.mode == "run")
    submits = sum(1 for e in executions if e.mode == "submit")
    successful_submits = [
        e for e in executions if e.mode == "submit" and e.status == "SUCCESS" and _all_passed(e)
    ]

    per_problem: dict = {}
    for execution in executions:
        entry = per_problem.setdefault(
            execution.problem_id,
            {"attempts": 0, "submits": 0, "completed": False},
        )
        entry["attempts"] += 1
        if execution.mode == "submit":
            entry["submits"] += 1
            if execution.status == "SUCCESS" and _all_passed(execution):
                entry["completed"] = True

    return {
        "totals": {
            "runs": runs,
            "submits": submits,
            "executions": len(executions),
            "success_rate": round(len(successful_submits) / submits, 3) if submits else None,
        },
        "problems": {
            "attempted": len(per_problem),
            "completed": sum(1 for v in per_problem.values() if v["completed"]),
        },
        "recent_activity": [
            {
                "problem_slug": problems_by_id[e.problem_id].slug,
                "problem_title": problems_by_id[e.problem_id].title,
                "mode": e.mode,
                "status": e.status,
                "passed": sum(1 for t in e.test_executions if t.passed),
                "total": len(e.test_executions),
                "runtime_ms": e.runtime_ms,
                "at": e.created_at.isoformat(),
            }
            for e in executions[:10]
        ],
        "per_problem": [
            {
                "problem_slug": problems_by_id[pid].slug,
                "problem_title": problems_by_id[pid].title,
                **entry,
            }
            for pid, entry in sorted(
                per_problem.items(),
                key=lambda item: item[1]["attempts"],
                reverse=True,
            )
        ][:20],
    }


def _all_passed(execution: Execution) -> bool:
    cases = execution.test_executions
    return bool(cases) and all(case.passed for case in cases)
