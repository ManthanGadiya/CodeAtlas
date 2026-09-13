"""AI Gateway — provider abstraction (docs/DESIGN.md §37, docs/AI_And_ML_Strategy.md §36).

The gateway keeps the tutor engine free of provider-specific code.
Core functionality must work without external AI (docs/PRD.md NFR-002);
missing keys therefore degrade to the deterministic template path, never
to a 500. LLM output is treated as untrusted — callers validate it.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Protocol

from app.core.config import get_settings


class GatewayUnavailable(RuntimeError):
    """Raised when no provider can fulfil the request."""


@dataclass(frozen=True)
class HintRequest:
    problem_title: str
    problem_slug: str
    problem_statement: str
    student_code: str | None
    mistake_code: str | None
    mistake_name: str | None
    hint_level: int
    intervention: str
    skill_hint: str | None


@dataclass(frozen=True)
class HintResponse:
    content: str
    provider: str
    model: str
    latency_ms: int
    # Deterministic fallback responses carry this flag so callers can
    # explain why the hint is template-based rather than LLM-generated.
    is_fallback: bool = False


class TutorProvider(Protocol):
    name: str

    def generate_hint(self, request: HintRequest) -> HintResponse: ...


# --- Deterministic fallback provider (always available) ----------------------


class DummyProvider:
    """Offline-safe provider that builds hints from mistake-aware templates.

    This is the Phase 3.1 "no-LLM" path.  Every hint is traceable to a
    rule in docs/Tutoring_Engine.md and docs/Mistake_Taxonomy.md.
    """

    name = "dummy"

    _TEMPLATES: dict[str, list[str]] = {
        # M01 Syntax Error
        "M01": [
            (
                "Look at the line the compiler pointed to — "
                "what token does Python expect there? Check brackets, colons, and indentation."
            ),
            (
                "The syntax error is near one line. Read the error message carefully: "
                "it tells you which symbol is missing."
            ),
            (
                "Python's syntax for this construct is `for i in range(...):` — "
                "compare it character by character to your line."
            ),
        ],
        # M03 Runtime Error
        "M03": [
            (
                "Your code crashed at runtime. "
                "What input could make that line fail? Try a tiny example by hand."
            ),
            (
                "A runtime error means the logic reached a bad state. "
                "What does the failing line assume about the data?"
            ),
            (
                "Trace the failing case step by step — "
                "which variable holds an unexpected value right before the crash?"
            ),
        ],
        # M04 Logic Error (ambiguous — keep generic, Socratic)
        "M04": [
            (
                "One of your visible cases is failing. Pick the first failing input "
                "and walk through your code by hand — what does it return versus what is expected?"
            ),
            (
                "Your output differs from expected. "
                "What invariant should hold after each iteration, and does your code keep it?"
            ),
            (
                "Compare expected vs actual for the failing case. "
                "Which branch of your logic produces the wrong value?"
            ),
        ],
        # M07 Complexity
        "M07": [
            (
                "Your solution is correct but may be too slow for large inputs. "
                "What operation dominates the runtime?"
            ),
            (
                "Count how many times the inner loop can run in terms of n — "
                "is there a way to avoid re-scanning?"
            ),
            (
                "Consider the constraints: which data structure could reduce "
                "the repeated work from O(n²) toward O(n) or O(n log n)?"
            ),
        ],
        # M10 Edge Case Failure
        "M10": [
            (
                "Your code passes the visible examples but fails a hidden edge case. "
                "What inputs are missing from the examples — empty, single element, "
                "duplicates, extremes?"
            ),
            (
                "Hidden failures often mean boundary handling. "
                "What should happen when the input is at its smallest or largest allowed value?"
            ),
            (
                "Write three tests that would break your current code: "
                "an empty case, a boundary case, and a duplicate case. Which one fails?"
            ),
        ],
    }

    _GENERIC: list[str] = [
        "What is the smallest input that could fail here? Try it before changing code.",
        (
            "Before editing, write one sentence: what do you believe is wrong "
            "and which test would prove it?"
        ),
        (
            "State the invariant your loop should maintain — "
            "then check whether your code actually keeps it."
        ),
    ]

    def generate_hint(self, request: HintRequest) -> HintResponse:
        start = time.monotonic()
        pool = self._TEMPLATES.get(request.mistake_code or "", self._GENERIC)
        # Clamp level to pool bounds; escalation = longer ladder → later entries
        idx = min(max(request.hint_level - 1, 0), len(pool) - 1) if request.hint_level > 0 else 0
        content = pool[idx]
        # Prepend skill-specific nudge when available (sub-skill personalization)
        if request.skill_hint and request.hint_level <= 2:
            content = f"Focus skill: {request.skill_hint}. {content}"
        latency_ms = int((time.monotonic() - start) * 1000)
        # Ensure at least 1ms so latency tracking is visibly non-zero
        latency_ms = max(latency_ms, 1)
        return HintResponse(
            content=content,
            provider=self.name,
            model="template-v1",
            latency_ms=latency_ms,
            is_fallback=True,
        )


# --- Stubbed cloud providers (wired for future keys, not used in V1 tests) ---


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def generate_hint(self, request: HintRequest) -> HintResponse:
        # Phase 3.1 does not ship live Gemini calls — the gateway will fall
        # through to DummyProvider. This stub exists so a future commit can
        # fill it without changing the gateway interface.
        raise GatewayUnavailable("Gemini provider not implemented in Phase 3.1")


class GroqProvider:
    name = "groq"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def generate_hint(self, request: HintRequest) -> HintResponse:
        raise GatewayUnavailable("Groq provider not implemented in Phase 3.1")


# --- Gateway router ----------------------------------------------------------


class TutorGateway:
    """Routes a HintRequest to the cheapest adequate provider."""

    def __init__(self, providers: list[TutorProvider], fallback: TutorProvider) -> None:
        self.providers = providers
        self.fallback = fallback

    def generate(self, request: HintRequest) -> HintResponse:
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                return provider.generate_hint(request)
            except GatewayUnavailable as exc:
                last_error = exc
                continue
            except Exception as exc:  # noqa: BLE001 — treat any provider failure as fallback
                last_error = exc
                continue
        # All cloud providers failed or none configured → deterministic fallback
        try:
            return self.fallback.generate_hint(request)
        except Exception as exc:  # noqa: BLE001
            raise GatewayUnavailable(f"All providers failed. Last error: {last_error}") from exc


def _build_providers() -> tuple[list[TutorProvider], TutorProvider]:
    settings = get_settings()
    providers: list[TutorProvider] = []
    # Gemini and Groq stay optional placeholders until the AI gateway milestone
    # where keys are validated and costs are tracked (docs/PRD.md).
    if settings.gemini_api_key:
        providers.append(GeminiProvider(settings.gemini_api_key))
    if settings.groq_api_key:
        providers.append(GroqProvider(settings.groq_api_key))
    fallback = DummyProvider()
    return providers, fallback


def get_gateway() -> TutorGateway:
    providers, fallback = _build_providers()
    return TutorGateway(providers=providers, fallback=fallback)


def hash_context(request: HintRequest) -> str:
    """Stable hash of the hint context for TutorInteraction.prompt_context_hash."""
    raw = (
        f"{request.problem_slug}|{request.mistake_code}|{request.hint_level}|"
        f"{request.intervention}|{(request.student_code or '')[:500]}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
