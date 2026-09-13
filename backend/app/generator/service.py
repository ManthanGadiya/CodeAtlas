"""Generator service — validated problem construction (Problem_Generator §59-69).

Pipeline per §59 / ROADMAP §24:
  Syntax → Test generation → Solution verification → Difficulty → Duplicate → Quality

V1 is rule-based + template mutations (docs §9: generate less, transform more).
LLM generation plugs behind the same interface when keys are present.
"""

from __future__ import annotations

import ast
import hashlib
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.problems.models import Problem, ProblemSkill, Skill, TestCase

MODEL_VERSION = "generator-rule-v1"

# ---------------------------------------------------------------------------
# Fingerprint / quality
# ---------------------------------------------------------------------------


def fingerprint_for(title: str, description: str, function_name: str, difficulty: str) -> str:
    raw = f"{title}\n{description}\n{function_name}\n{difficulty}".lower().strip().encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def estimate_quality(description: str, tests: list[dict]) -> float:
    """Simple heuristic Quality (§63): correctness+clarity+test quality - ambiguity."""
    score = 0.0
    if len(description) >= 80:
        score += 0.3
    if len(description) >= 200:
        score += 0.1
    if any(t.get("visibility") == "visible" for t in tests):
        score += 0.2
    if any(t.get("visibility") == "hidden" for t in tests):
        score += 0.2
    if len(tests) >= 4:
        score += 0.15
    if len({t.get("name") for t in tests}) == len(tests):
        score += 0.05
    return round(min(1.0, score), 2)


# ---------------------------------------------------------------------------
# Validation helpers (pure where possible)
# ---------------------------------------------------------------------------


def validate_syntax(code: str) -> str | None:
    if not code or not code.strip():
        return "starter_code must not be empty"
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return f"syntax error: {exc.msg} at line {exc.lineno}"
    return None


def validate_tests(tests: list[dict]) -> str | None:
    if not tests:
        return "at least one test case required"
    if len(tests) > 20:
        return "too many test cases (max 20)"
    names = [t.get("name") for t in tests]
    if len(names) != len(set(names)):
        return "duplicate test names"
    for t in tests:
        if not t.get("name"):
            return "each test needs a name"
        if "input_args" not in t or "expected_output" not in t:
            return f"test {t.get('name')} missing input_args/expected_output"
        if not isinstance(t["input_args"], list):
            return f"test {t['name']} input_args must be a list"
        if t.get("visibility") not in (None, "visible", "hidden"):
            return f"test {t['name']} invalid visibility"
        if t.get("test_type") not in (None, "normal", "edge", "boundary"):
            return f"test {t['name']} invalid test_type"
    visible = [t for t in tests if t.get("visibility") == "visible"]
    hidden = [t for t in tests if t.get("visibility") == "hidden"]
    if not visible:
        return "at least one visible test required"
    if not hidden:
        return "at least one hidden test required"
    return None


def validate_difficulty(difficulty: str) -> str | None:
    if difficulty not in ("easy", "medium", "hard"):
        return "difficulty must be easy | medium | hard"
    return None


# Reference solutions used to verify mutated tests still pass.
REFERENCE_SOLUTIONS: dict[str, str] = {
    "two-sum": (
        "def two_sum(nums, target):\n"
        "    seen = {}\n"
        "    for i, n in enumerate(nums):\n"
        "        need = target - n\n"
        "        if need in seen:\n"
        "            a, b = seen[need], i\n"
        "            return [a, b] if a < b else [b, a]\n"
        "        seen[n] = i\n"
        "    return []\n"
    ),
    "binary-search-first-occurrence": (
        "def first_occurrence(nums, target):\n"
        "    lo, hi, ans = 0, len(nums)-1, -1\n"
        "    while lo <= hi:\n"
        "        mid = (lo+hi)//2\n"
        "        if nums[mid] == target:\n"
        "            ans = mid\n"
        "            hi = mid-1\n"
        "        elif nums[mid] < target:\n"
        "            lo = mid+1\n"
        "        else:\n"
        "            hi = mid-1\n"
        "    return ans\n"
    ),
    "valid-parentheses": (
        "def is_valid(s):\n"
        "    m = {')':'(', ']':'[', '}':'{'}\n"
        "    st=[]\n"
        "    for ch in s:\n"
        "        if ch in '([{': st.append(ch)\n"
        "        elif not st or st[-1]!=m[ch]: return False\n"
        "        else: st.pop()\n"
        "    return not st\n"
    ),
    "maximum-subarray": (
        "def max_subarray_sum(nums):\n"
        "    best=cur=nums[0]\n"
        "    for n in nums[1:]:\n"
        "        cur = max(n, cur+n)\n"
        "        best = max(best, cur)\n"
        "    return best\n"
    ),
    "valid-palindrome": (
        "def is_palindrome(s):\n"
        "    t=''.join(ch.lower() for ch in s if ch.isalnum())\n"
        "    return t==t[::-1]\n"
    ),
}

# Map function names to canonical solution key via problem slug
SLUG_BY_FUNCTION: dict[str, str] = {
    "two_sum": "two-sum",
    "first_occurrence": "binary-search-first-occurrence",
    "is_valid": "valid-parentheses",
    "max_subarray_sum": "maximum-subarray",
    "is_palindrome": "valid-palindrome",
}


def _reference_for_slug(slug: str, function_name: str) -> str | None:
    if slug in REFERENCE_SOLUTIONS:
        return REFERENCE_SOLUTIONS[slug]
    return REFERENCE_SOLUTIONS.get(SLUG_BY_FUNCTION.get(function_name, ""))


# ---------------------------------------------------------------------------
# Execution validation (needs runner)
# ---------------------------------------------------------------------------


def verify_solution(code: str, function_name: str, tests: list[dict], runner) -> str | None:
    """Run reference solution via runner; return error string or None on success."""
    if runner is None:
        return "runner unavailable"
    outcome = runner.run(code=code, function_name=function_name, tests=tests)
    if outcome.load_error:
        return f"solution load_error: {outcome.load_error}"
    if outcome.status != "SUCCESS":
        return f"solution execution status {outcome.status}"
    for r in outcome.results or []:
        if not r.get("passed"):  # noqa: E501
            return f"solution failed test {r.get('name')}: expected {r.get('expected')} got {r.get('actual')}"  # noqa: E501
    return None


# ---------------------------------------------------------------------------
# Mutation templates (§8-9, §34)
# ---------------------------------------------------------------------------

MUTATION_TYPES = ("boundary_variant", "constraint_tighten", "context_shift")


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80].strip("-")


def apply_mutation(source: Problem, mutation_type: str) -> dict:
    """Return draft fields derived from source + mutation."""
    if mutation_type not in MUTATION_TYPES:
        raise ValueError(f"unknown mutation_type {mutation_type}")

    base_title = source.title
    base_desc = source.description
    base_slug = source.slug
    base_tests = [
        {
            "name": t.name,
            "input_args": t.input_args,
            "expected_output": t.expected_output,
            "visibility": t.visibility,
            "test_type": t.test_type,
        }
        for t in source.test_cases
    ]

    if mutation_type == "boundary_variant":
        title = f"{base_title} — Boundary Variant"
        desc = base_desc + (
            "\n\n**Variant focus:** Pay special attention to edge cases "
            "(empty input, single element, all identical values, boundaries)."
        )
        # Ensure an empty/single test is present as hidden if missing
        names = {t["name"] for t in base_tests}
        extra = []
        if "mutated-empty" not in names and source.function_name in (
            "first_occurrence",
            "is_valid",
            "is_palindrome",
        ):
            # Generic empty expectation derived from existing behavior
            empty_map = {
                "first_occurrence": {"input_args": [[], 1], "expected_output": -1},
                "is_valid": {"input_args": [""], "expected_output": True},
                "is_palindrome": {"input_args": [""], "expected_output": True},
            }
            cfg = empty_map.get(source.function_name)
            if cfg:
                extra.append(
                    {"name": "mutated-empty", "visibility": "hidden", "test_type": "edge", **cfg}
                )
        tests = base_tests + extra
        difficulty = source.difficulty

    elif mutation_type == "constraint_tighten":
        title = f"{base_title} — Tight Constraints"
        desc = base_desc + (
            "\n\n**Tightened constraints:** `n ≤ 10^5` and time limit is strict — "
            "O(n log n) or better is expected. Brute force will time out."
        )
        tests = base_tests
        # Promote difficulty one step
        promo = {"easy": "medium", "medium": "hard", "hard": "hard"}
        difficulty = promo.get(source.difficulty, source.difficulty)

    elif mutation_type == "context_shift":  # transfer surface change (§49)
        title = f"{base_title} — Transfer Context"
        # Swap generic phrasing to transaction/pipeline context
        desc = base_desc.replace("array of integers", "sequence of transaction counts").replace(
            "array", "sequence"
        )
        if desc == base_desc:
            desc = base_desc + (
                "\n\n**Transfer context:** Same algorithm, different story — "
                "apply the core idea in a new domain."
            )
        tests = base_tests
        difficulty = source.difficulty
    else:
        raise ValueError("unreachable")

    slug = f"{base_slug}-{mutation_type}-{uuid.uuid4().hex[:6]}"
    return {
        "slug": slug,
        "title": title,
        "description": desc,
        "function_name": source.function_name,
        "difficulty": difficulty,
        "starter_code": source.starter_code,
        "tests": tests,
        "source_slug": base_slug,
        "source_id": source.id,
        "skills": [(link.skill.slug, link.role, link.importance) for link in source.skill_links],
    }


# ---------------------------------------------------------------------------
# Orchestration (build + validate + persist)
# ---------------------------------------------------------------------------


class GenerationError(ValueError):
    pass


def validate_draft(
    *,
    title: str,
    description: str,
    function_name: str,
    difficulty: str,
    starter_code: str,
    tests: list[dict],
    slug: str | None = None,
    db: Session | None = None,
    runner=None,
    reference_code: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if not title or len(title.strip()) < 3:
        errors.append("title too short")
    if not description or len(description.strip()) < 40:
        errors.append("description too short (min 40 chars)")
    if not function_name or not re.match(r"^[a-z_][a-z0-9_]*$", function_name):
        errors.append("invalid function_name")
    if (err := validate_difficulty(difficulty)) is not None:
        errors.append(err)
    if (err := validate_syntax(starter_code)) is not None:
        errors.append(err)
    if reference_code is not None and (err := validate_syntax(reference_code)) is not None:
        errors.append(f"reference_code {err}")
    if (err := validate_tests(tests)) is not None:
        errors.append(err)
    if slug and db is not None:
        exists = db.scalar(select(Problem).where(Problem.slug == slug))
        if exists:
            errors.append("slug already exists")
    # Fingerprint duplicate check requires full problem fingerprint
    if title and description and function_name and difficulty and db is not None:
        fp = fingerprint_for(title, description, function_name, difficulty)
        dup = db.scalar(select(Problem).where(Problem.fingerprint == fp))
        if dup:
            errors.append(f"duplicate fingerprint of {dup.slug}")
    # Solution verification last (needs runner)
    if reference_code and not errors:
        err = verify_solution(reference_code, function_name, tests, runner)
        if err:
            errors.append(err)
    # Quality gate (§63)
    q = estimate_quality(description, tests)
    if q < 0.5:
        errors.append(f"quality_score {q} below threshold 0.5")
    return errors


def _get_skill_map(db: Session) -> dict[str, Skill]:
    return {s.slug: s for s in db.scalars(select(Skill)).all()}


def create_problem_from_draft(
    db: Session,
    *,
    slug: str,
    title: str,
    description: str,
    function_name: str,
    difficulty: str,
    starter_code: str,
    tests: list[dict],
    skills: list[tuple[str, str, float]],
    source_type: str = "generated",
    parent_problem_id: uuid.UUID | None = None,
    generation_metadata: dict | None = None,
) -> Problem:
    fp = fingerprint_for(title, description, function_name, difficulty)
    q = estimate_quality(description, tests)
    problem = Problem(
        slug=slug,
        title=title,
        description=description,
        difficulty=difficulty,
        language="python",
        source_type=source_type,
        starter_code=starter_code,
        function_name=function_name,
        estimated_minutes=20 if difficulty == "easy" else 30,
        fingerprint=fp,
        parent_problem_id=parent_problem_id,
        generation_metadata=generation_metadata,
        quality_score=q,
    )
    db.add(problem)
    db.flush()
    skill_map = _get_skill_map(db)
    for slug_s, role, importance in skills:
        skill = skill_map.get(slug_s)
        if not skill:
            continue
        link = ProblemSkill(
            problem_id=problem.id, skill_id=skill.id, role=role, importance=importance
        )
        db.add(link)
    for idx, t in enumerate(tests):
        tc = TestCase(
            problem_id=problem.id,
            name=t["name"],
            input_args=t["input_args"],
            expected_output=t["expected_output"],
            visibility=t.get("visibility", "hidden"),
            test_type=t.get("test_type", "normal"),
            order_index=idx,
        )
        db.add(tc)
    db.commit()
    db.refresh(problem)
    return problem


def mutate_problem(
    db: Session,
    *,
    source_slug: str,
    mutation_type: str,
    student_id: uuid.UUID | None = None,
    runner=None,
) -> Problem:
    source = db.scalar(
        select(Problem)
        .where(Problem.slug == source_slug)
        .options(
            selectinload(Problem.skill_links).selectinload(ProblemSkill.skill),
            selectinload(Problem.test_cases),
        )
    )
    if not source:
        raise GenerationError("source problem not found")
    draft = apply_mutation(source, mutation_type)
    ref_code = _reference_for_slug(source.slug, source.function_name)
    # Validate draft before persisting
    errors = validate_draft(
        title=draft["title"],
        description=draft["description"],
        function_name=draft["function_name"],
        difficulty=draft["difficulty"],
        starter_code=draft["starter_code"],
        tests=draft["tests"],
        slug=draft["slug"],
        db=db,
        runner=runner,
        reference_code=ref_code,
    )
    if errors:
        raise GenerationError("; ".join(errors))
    problem = create_problem_from_draft(
        db,
        slug=draft["slug"],
        title=draft["title"],
        description=draft["description"],
        function_name=draft["function_name"],
        difficulty=draft["difficulty"],
        starter_code=draft["starter_code"],
        tests=draft["tests"],
        skills=draft["skills"],
        source_type="generated",
        parent_problem_id=source.id,
        generation_metadata={
            "mutation_type": mutation_type,
            "source_slug": source.slug,
            "model_version": MODEL_VERSION,
            "creator_student_id": str(student_id) if student_id else None,
            "generated_at": datetime.now(UTC).isoformat(),
        },
    )
    # Emit learning event for evaluation (§53)
    if student_id:
        try:
            from app.events.service import record_event

            record_event(
                db,
                student_id=student_id,
                event_type="PROBLEM_GENERATED",
                payload={
                    "slug": problem.slug,
                    "mutation_type": mutation_type,
                    "source_slug": source.slug,
                    "fingerprint": problem.fingerprint,
                    "quality_score": problem.quality_score,
                },
            )
        except Exception:
            pass
    return problem
