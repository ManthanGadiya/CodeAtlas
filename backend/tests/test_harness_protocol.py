"""Harness protocol tests — run the sandbox script directly, no Docker.

These verify the stdin/stdout contract between host runner and container
harness: mixed student output, sentinel parsing, per-test isolation,
syntax vs runtime load errors, and bool/int comparison strictness.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.execution.runner import _parse_results

HARNESS = Path(__file__).resolve().parents[1] / "sandbox" / "harness.py"


def run_harness(payload: dict) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, str(HARNESS)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.returncode, completed.stdout


def parse_block(stdout: str) -> dict:
    results, load_error = _parse_results(stdout)
    assert results is not None or load_error is not None, "no sentinel block found"
    if results is not None:
        return {"results": results}
    return {"load_error": load_error}


def test_passing_suite():
    code, stdout = run_harness(
        {
            "code": "def add(a, b):\n    return a + b\n",
            "function_name": "add",
            "tests": [
                {"name": "t1", "input_args": [1, 2], "expected_output": 3},
                {"name": "t2", "input_args": [-1, 1], "expected_output": 0},
            ],
        }
    )
    payload = parse_block(stdout)
    assert code == 0
    assert all(r["passed"] for r in payload["results"])
    assert payload["results"][0]["actual"] == 3


def test_failing_case_reports_actual_and_expected_mismatch():
    code, stdout = run_harness(
        {
            "code": "def add(a, b):\n    return a + b + 1\n",
            "function_name": "add",
            "tests": [{"name": "t1", "input_args": [1, 2], "expected_output": 3}],
        }
    )
    payload = parse_block(stdout)
    result = payload["results"][0]
    assert not result["passed"]
    assert result["actual"] == 4


def test_exception_in_one_test_does_not_kill_the_rest():
    code_with_raising_branch = (
        "def boom(x):\n    if x == 0:\n        raise ValueError('nope')\n    return x\n"
    )
    code, stdout = run_harness(
        {
            "code": code_with_raising_branch,
            "function_name": "boom",
            "tests": [
                {"name": "zero", "input_args": [0], "expected_output": 0},
                {"name": "five", "input_args": [5], "expected_output": 5},
            ],
        }
    )
    payload = parse_block(stdout)
    zero = next(r for r in payload["results"] if r["name"] == "zero")
    five = next(r for r in payload["results"] if r["name"] == "five")
    assert "ValueError" in zero["error"]
    assert five["passed"]


def test_syntax_error_is_classified():
    _, stdout = run_harness(
        {
            "code": "def broken(:\n    pass\n",
            "function_name": "broken",
            "tests": [],
        }
    )
    payload = parse_block(stdout)
    assert payload["load_error"]["kind"] == "syntax"
    assert "line" in payload["load_error"]["message"]


def test_import_time_exception_is_classified():
    _, stdout = run_harness(
        {
            "code": "raise RuntimeError('boom at import')\n",
            "function_name": "anything",
            "tests": [],
        }
    )
    payload = parse_block(stdout)
    assert payload["load_error"]["kind"] == "exception"
    assert "RuntimeError" in payload["load_error"]["message"]


def test_missing_function_is_reported():
    _, stdout = run_harness(
        {
            "code": "x = 1\n",
            "function_name": "not_defined",
            "tests": [],
        }
    )
    payload = parse_block(stdout)
    assert "not_defined" in payload["load_error"]["message"]


def test_bool_int_conflation_is_rejected():
    _, stdout = run_harness(
        {
            "code": "def f():\n    return True\n",
            "function_name": "f",
            "tests": [{"name": "t", "input_args": [], "expected_output": 1}],
        }
    )
    payload = parse_block(stdout)
    assert payload["results"][0]["passed"] is False


def test_student_print_output_precedes_sentinel_and_parses():
    _, stdout = run_harness(
        {
            "code": "print('hello world')\nprint('[1, 2]')\n\ndef f():\n    return 7\n",
            "function_name": "f",
            "tests": [{"name": "t", "input_args": [], "expected_output": 7}],
        }
    )
    assert stdout.startswith("hello world")
    payload = parse_block(stdout)
    assert payload["results"][0]["passed"]


@pytest.mark.parametrize(
    "stdout",
    [
        "",
        "garbage without sentinel",
        "<<<CODEATLAS_RESULTS>>>\n{not json}",
    ],
)
def test_parse_results_returns_none_on_garbage(stdout):
    results, load_error = _parse_results(stdout)
    assert results is None and load_error is None
