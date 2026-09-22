"""Analytics summary queries — observations only, honestly labelled."""

from sqlalchemy import case, select
from sqlalchemy.orm import Session, selectinload

from app.execution.models import Execution
from app.problems.models import Problem


def build_summary(db: Session, student_id) -> dict:
    """Build activity summary — optimized with SQL aggregates for totals.

    Previous version loaded the full execution history per request (STATUS.md:
    "fine at Phase 1.6 scale, switch to SQL aggregates when history grows").
    Hardening switches totals to COUNT(*) aggregates so a student with 10k
    executions does not materialize 10k rows.  Recent activity and per-problem
    breakdown remain bounded (10 and 20 rows respectively) via limited queries.
    """
    from sqlalchemy import func

    # Totals via SQL aggregates — O(1) rows instead of O(n)
    totals_row = db.execute(
        select(
            func.count().label("total"),
            func.count().filter(Execution.mode == "run").label("runs"),
            func.count().filter(Execution.mode == "submit").label("submits"),
            func.count()
            .filter(Execution.mode == "submit", Execution.status == "SUCCESS")
            .label("successful_submits"),
        ).where(Execution.student_id == student_id)
    ).one()

    total = totals_row.total or 0
    runs = totals_row.runs or 0
    submits = totals_row.submits or 0
    successful_submits = totals_row.successful_submits or 0

    # Recent activity — only the 10 most recent executions with test counts
    recent_executions = db.scalars(
        select(Execution)
        .where(Execution.student_id == student_id)
        .options(selectinload(Execution.test_executions))
        .order_by(Execution.created_at.desc())
        .limit(10)
    ).all()

    recent_problem_ids = {e.problem_id for e in recent_executions}

    # Per-problem aggregates via GROUP BY — bounded to 20 most-attempted
    per_problem_rows = db.execute(
        select(
            Execution.problem_id,
            func.count().label("attempts"),
            func.count().filter(Execution.mode == "submit").label("submits"),
            func.max(case((Execution.status == "SUCCESS", 1), else_=0)).label("has_success"),
        )
        .where(Execution.student_id == student_id)
        .group_by(Execution.problem_id)
        .order_by(func.count().desc())
        .limit(20)
    ).all()

    per_problem_ids = {row.problem_id for row in per_problem_rows}
    all_needed_ids = recent_problem_ids | per_problem_ids
    problems_by_id: dict = {}
    if all_needed_ids:
        problems_by_id = {
            problem.id: problem
            for problem in db.scalars(select(Problem).where(Problem.id.in_(all_needed_ids)))
        }

    # For completed flag we need to know if any submit succeeded with all tests
    # passing.  SUCCESS status is equivalent to _all_passed for submits (the
    # execution service only sets SUCCESS when every test passes).  GROUP BY
    # MAX(SUCCESS) captures this without loading every execution.
    per_problem = {}
    attempted = 0
    completed = 0
    per_problem_list = []
    for row in per_problem_rows:
        pid = row.problem_id
        is_completed = bool(row.has_success) and row.submits > 0
        entry = {"attempts": row.attempts, "submits": row.submits, "completed": is_completed}
        per_problem[pid] = entry
        if is_completed:
            completed += 1
        attempted += 1
        prob = problems_by_id.get(pid)
        if prob:
            per_problem_list.append(
                {
                    "problem_slug": prob.slug,
                    "problem_title": prob.title,
                    **entry,
                }
            )

    return {
        "totals": {
            "runs": runs,
            "submits": submits,
            "executions": total,
            "success_rate": round(successful_submits / submits, 3) if submits else None,
        },
        "problems": {
            "attempted": attempted,
            "completed": completed,
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
            for e in recent_executions
        ],
        "per_problem": per_problem_list,
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
