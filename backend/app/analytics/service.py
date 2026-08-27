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


def build_learner_summary(db: Session, student_id) -> dict:
    """The learner model's first read surface (Phase 2.6 data contract).

    Skill states, open mistakes, and recurrence patterns — the personalized
    counterpart to the raw activity summary above. Skills are returned
    weakest-first because that is what a student or curriculum needs most;
    low-confidence states are labelled UNKNOWN rather than weak
    (docs/Learning_Model.md §34: missing evidence is never weakness).
    """
    from app.behavior.models import BehaviorPattern
    from app.mistakes.models import Mistake, MistakeCategory, MistakePattern
    from app.problems.models import Problem, Skill
    from app.skills.models import StudentSkillState

    states = db.execute(
        select(StudentSkillState, Skill)
        .join(Skill, Skill.id == StudentSkillState.skill_id)
        .where(StudentSkillState.student_id == student_id)
        .order_by(StudentSkillState.mastery)
    ).all()

    open_mistakes = db.execute(
        select(Mistake, MistakeCategory, Problem)
        .join(MistakeCategory, MistakeCategory.id == Mistake.category_id)
        .join(Problem, Problem.id == Mistake.problem_id)
        .where(Mistake.student_id == student_id, Mistake.resolution_status == "UNRESOLVED")
        .order_by(Mistake.detected_at.desc())
    ).all()

    mistake_patterns = db.execute(
        select(MistakePattern, MistakeCategory, Skill)
        .join(MistakeCategory, MistakeCategory.id == MistakePattern.category_id)
        .join(Skill, Skill.id == MistakePattern.skill_id)
        .where(MistakePattern.student_id == student_id)
        .order_by(MistakePattern.occurrence_count.desc())
    ).all()

    behavior_patterns = db.scalars(
        select(BehaviorPattern)
        .where(BehaviorPattern.student_id == student_id)
        .order_by(BehaviorPattern.last_observed_at.desc())
    ).all()

    return {
        "skills": [
            {
                "skill_slug": skill.slug,
                "skill_name": skill.name,
                "mastery": round(state.mastery, 3),
                "confidence": round(state.confidence, 3),
                # Below this confidence the estimate is closer to a guess
                # than a measurement; consumers must show UNKNOWN, not weak.
                "reliability": "unknown" if state.confidence < 0.5 else "estimated",
                "evidence_count": state.evidence_count,
                "retention": state.retention,
                "last_practiced_at": (
                    state.last_practiced_at.isoformat() if state.last_practiced_at else None
                ),
            }
            for state, skill in states
        ],
        "open_mistakes": [
            {
                "category_code": category.code,
                "category_name": category.name,
                "problem_slug": problem.slug,
                "severity": mistake.severity,
                "confidence": mistake.confidence,
                "evidence_note": mistake.evidence_note,
                "detected_at": mistake.detected_at.isoformat(),
            }
            for mistake, category, problem in open_mistakes
        ],
        "mistake_patterns": [
            {
                "category_code": category.code,
                "category_name": category.name,
                "skill_slug": skill.slug,
                "occurrence_count": pattern.occurrence_count,
                "confidence": pattern.confidence,
                "last_seen_at": pattern.last_seen_at.isoformat(),
            }
            for pattern, category, skill in mistake_patterns
        ],
        "behavior_patterns": [
            {
                "behavior_type": pattern.behavior_type,
                "frequency": pattern.frequency,
                "severity": pattern.severity,
                "trend": pattern.trend,
                "confidence": pattern.confidence,
                "last_observed_at": pattern.last_observed_at.isoformat(),
            }
            for pattern in behavior_patterns
        ],
    }
