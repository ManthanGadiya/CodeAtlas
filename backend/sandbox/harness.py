"""In-sandbox test harness.

Runs INSIDE the execution container against untrusted student code.
Protocol (shared with backend/app/execution/runner.py):

    stdin :  {"code": ..., "function_name": ...,
              "tests": [{name, input_args, expected_output}, ...]}
    stdout:  arbitrary student output, then
             <<<CODEATLAS_RESULTS>>>
             {"results": [...]}   or   {"load_error": {...}}

Student code runs in a fresh namespace; per-test exceptions are captured
individually so one failing case does not abort the rest. A runaway loop
cannot hang forever — the host enforces a wall-clock timeout and
force-removes the container.

Trust note (accepted for V1): because harness and solution share one
process, deliberately malicious student code could forge the results
block. CodeAtlas is a personal tutor — grading integrity threats come
from outside, not from the single student hacking their own tool.
"""

import json
import sys
import traceback

RESULTS_SENTINEL = "<<<CODEATLAS_RESULTS>>>"


def _emit(payload: dict) -> None:
    sys.stdout.write(RESULTS_SENTINEL + "\n")
    sys.stdout.write(json.dumps(payload))
    sys.stdout.write("\n")
    sys.stdout.flush()


def _safe(value):
    """Make an arbitrary return value JSON-serializable; fall back to repr."""
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return repr(value)


def _same(actual, expected) -> bool:
    """Comparison strict enough for teaching feedback.

    Guards against Python's bool/int conflation (True == 1) while still
    treating ints and floats as numerically comparable (5 == 5.0).
    """
    if isinstance(actual, bool) != isinstance(expected, bool):
        return False
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return actual == expected
    if type(actual) is not type(expected):
        return False
    return actual == expected


def main() -> int:
    payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    function_name = payload["function_name"]
    namespace: dict = {}

    try:
        compiled = compile(payload["code"], "solution.py", "exec")
        exec(compiled, namespace)  # noqa: S102 — executing student code is the purpose
    except SyntaxError as exc:
        _emit(
            {
                "load_error": {
                    "kind": "syntax",
                    "message": f"SyntaxError: {exc.msg} (line {exc.lineno})",
                }
            }
        )
        return 0
    except BaseException as exc:  # student code may raise anything at import time
        _emit(
            {
                "load_error": {
                    "kind": "exception",
                    "message": f"{type(exc).__name__}: {exc}",
                }
            }
        )
        return 0

    function = namespace.get(function_name)
    if not callable(function):
        _emit(
            {
                "load_error": {
                    "kind": "exception",
                    "message": f"No callable named '{function_name}' was defined.",
                }
            }
        )
        return 0

    results = []
    for test in payload["tests"]:
        entry = {"name": test["name"], "passed": False, "actual": None, "error": None}
        try:
            actual = function(*test["input_args"])
            entry["actual"] = _safe(actual)
            entry["passed"] = _same(actual, test["expected_output"])
        except BaseException as exc:  # per-test isolation
            entry["error"] = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        results.append(entry)

    _emit({"results": results})
    return 0


if __name__ == "__main__":
    sys.exit(main())
