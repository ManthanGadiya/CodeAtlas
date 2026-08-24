"""Docker-isolated Python runner.

Security boundary (docs/Security_Privacy_And_Ethics.md §25-36, FR-004):
student code NEVER executes on the application host. Every run spawns a
container with:

    --network none          no network access at all
    --memory/--memory-swap  hard memory cap, swap disabled (OOM -> exit 137)
    --cpus                  CPU ceiling
    --pids-limit            fork-bomb protection
    --init                  reaps orphaned children (zombie protection)
    --read-only + tmpfs     immutable root filesystem, tiny scratch /tmp
    --cap-drop ALL          no kernel capabilities
    --no-new-privileges     no privilege escalation
    non-root user           uid/gid 65534 (nobody)

The harness is mounted read-only; the submission and test data arrive via
stdin, results come back as a sentinel-delimited JSON block at the end of
stdout. Host-side protections: wall-clock timeout with forced container
removal, and bounded TAIL-KEEPING capture of both streams — a program that
floods output cannot exhaust host memory, and the trailing results block
survives truncation. Streams are decoded as UTF-8 with replacement so
non-ASCII student output cannot crash the runner regardless of host locale.
"""

import json
import subprocess
import threading
import time
import uuid as uuid_module
from collections import deque
from pathlib import Path

from app.core.config import Settings, get_settings

RESULTS_SENTINEL = "<<<CODEATLAS_RESULTS>>>"

# backend/app/execution/runner.py -> backend/sandbox/
HARNESS_DIR = Path(__file__).resolve().parents[2] / "sandbox"

_STATUS_SUCCESS = "SUCCESS"
_STATUS_COMPILE_ERROR = "COMPILE_ERROR"
_STATUS_RUNTIME_ERROR = "RUNTIME_ERROR"
_STATUS_TIMEOUT = "TIMEOUT"
_STATUS_MEMORY_LIMIT = "MEMORY_LIMIT"
_STATUS_SYSTEM_ERROR = "SYSTEM_ERROR"

_STDERR_IMAGE_MISSING = "unable to find image"
_PUMP_CHUNK = 65_536
_DOCKER_CLI_TIMEOUT_GRACE_SECONDS = 2


class RunnerUnavailableError(Exception):
    """Raised when the Docker engine or runner image cannot be used."""


class RunOutcome:
    def __init__(
        self,
        *,
        status: str,
        runtime_ms: int | None = None,
        exit_code: int | None = None,
        stdout_tail: str = "",
        stderr_tail: str = "",
        results: list[dict] | None = None,
        load_error: dict | None = None,
    ) -> None:
        self.status = status
        self.runtime_ms = runtime_ms
        self.exit_code = exit_code
        self.stdout_tail = stdout_tail
        self.stderr_tail = stderr_tail
        self.results = results or []
        self.load_error = load_error


class _TailBuffer:
    """Bounded buffer keeping the MOST RECENT bytes (the results block lives there)."""

    def __init__(self, max_bytes: int) -> None:
        self._chunks: deque[bytes] = deque()
        self._size = 0
        self._max_bytes = max_bytes

    def append(self, chunk: bytes) -> None:
        self._chunks.append(chunk)
        self._size += len(chunk)
        while self._size > self._max_bytes and self._chunks:
            dropped = self._chunks.popleft()
            self._size -= len(dropped)

    def value(self) -> str:
        return b"".join(self._chunks).decode("utf-8", errors="replace")


def _display_tail(text: str, limit: int) -> str:
    return text[-limit:] if len(text) > limit else text


def build_run_command(settings: Settings, container_name: str) -> list[str]:
    """Pure function so CI can unit-test the security-critical flags."""
    return [
        "docker",
        "run",
        "--rm",
        "--name",
        container_name,
        "--interactive",
        "--network",
        "none",
        "--memory",
        f"{settings.exec_memory_mb}m",
        "--memory-swap",
        f"{settings.exec_memory_mb}m",
        "--cpus",
        str(settings.exec_cpus),
        "--pids-limit",
        str(settings.exec_pids_limit),
        "--init",
        "--read-only",
        "--tmpfs",
        "/tmp:size=8m,noexec,nosuid,nodev",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--user",
        "65534:65534",
        "--env",
        "PYTHONDONTWRITEBYTECODE=1",
        "--volume",
        f"{HARNESS_DIR}:/sandbox:ro",
        settings.docker_image,
        "python",
        "-S",
        "/sandbox/harness.py",
    ]


def _parse_results(stdout: str) -> tuple[list[dict] | None, dict | None]:
    """Extract the sentinel block from mixed student/harness output."""
    index = stdout.rfind(RESULTS_SENTINEL)
    if index == -1:
        return None, None
    tail = stdout[index + len(RESULTS_SENTINEL) :].strip()
    try:
        payload = json.loads(tail.splitlines()[0]) if tail else json.loads(tail)
    except (ValueError, IndexError):
        try:
            payload = json.loads(tail)
        except ValueError:
            return None, None

    if "load_error" in payload:
        return None, payload["load_error"]
    if isinstance(payload.get("results"), list):
        return payload["results"], None
    return None, None


class DockerPythonRunner:
    """Executes one submission against a set of tests inside a container."""

    def run(self, *, code: str, function_name: str, tests: list[dict]) -> RunOutcome:
        settings = get_settings()
        self._ensure_image_available(settings.docker_image)

        payload = json.dumps(
            {
                "code": code,
                "function_name": function_name,
                "tests": [
                    {
                        "name": test["name"],
                        "input_args": test["input_args"],
                        "expected_output": test["expected_output"],
                    }
                    for test in tests
                ],
            }
        ).encode("utf-8")

        container_name = f"codeatlas-exec-{uuid_module.uuid4().hex[:12]}"
        command = build_run_command(settings, container_name)

        # Generous capture ceiling: bounded host memory, tail-kept so the
        # sentinel block survives even after megabytes of student printing.
        capture_cap = max(4 * settings.exec_output_limit_bytes, 262_144)
        stdout_buffer = _TailBuffer(capture_cap)
        stderr_buffer = _TailBuffer(capture_cap)

        started = time.monotonic()
        timed_out = False

        process = subprocess.Popen(  # noqa: S603 — fixed argv, no shell
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        def _pump(stream, buffer: _TailBuffer) -> None:
            try:
                while True:
                    chunk = stream.read(_PUMP_CHUNK)
                    if not chunk:
                        break
                    buffer.append(chunk)
            finally:
                stream.close()

        threads = [
            threading.Thread(target=_pump, args=(process.stdout, stdout_buffer)),
            threading.Thread(target=_pump, args=(process.stderr, stderr_buffer)),
            threading.Thread(target=self._feed_stdin, args=(process, payload)),
        ]
        for thread in threads:
            thread.daemon = True
            thread.start()

        try:
            process.wait(timeout=settings.exec_timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait(timeout=5)
            self._force_remove(container_name)

        runtime_ms = int((time.monotonic() - started) * 1000)
        for thread in threads:
            thread.join(timeout=5)

        stdout = stdout_buffer.value()
        stderr = stderr_buffer.value()
        display_limit = settings.exec_output_limit_bytes

        if timed_out:
            return RunOutcome(status=_STATUS_TIMEOUT, runtime_ms=runtime_ms)

        results, load_error = _parse_results(stdout)

        if results is not None or load_error is not None:
            # Trust parsed harness output over the container exit code: a
            # student-registered atexit hook can flip the exit code after
            # perfect results were already produced.
            if load_error is not None:
                status = (
                    _STATUS_COMPILE_ERROR
                    if load_error.get("kind") == "syntax"
                    else _STATUS_RUNTIME_ERROR
                )
            else:
                status = _STATUS_SUCCESS
            return RunOutcome(
                status=status,
                runtime_ms=runtime_ms,
                exit_code=process.returncode,
                stdout_tail=_display_tail(stdout, display_limit),
                stderr_tail=_display_tail(stderr, display_limit),
                results=results or [],
                load_error=load_error,
            )

        if process.returncode == 0:
            return RunOutcome(
                status=_STATUS_SYSTEM_ERROR,
                runtime_ms=runtime_ms,
                exit_code=process.returncode,
                stdout_tail=_display_tail(stdout, display_limit),
                stderr_tail=_display_tail(stderr, display_limit),
            )

        if process.returncode == 137:
            return RunOutcome(
                status=_STATUS_MEMORY_LIMIT,
                runtime_ms=runtime_ms,
                exit_code=process.returncode,
                stdout_tail=_display_tail(stdout, display_limit),
                stderr_tail=_display_tail(stderr, display_limit),
            )

        return RunOutcome(
            status=_STATUS_RUNTIME_ERROR,
            runtime_ms=runtime_ms,
            exit_code=process.returncode,
            stdout_tail=_display_tail(stdout, display_limit),
            stderr_tail=_display_tail(stderr, display_limit),
        )

    @staticmethod
    def _feed_stdin(process: subprocess.Popen, payload: bytes) -> None:
        try:
            process.stdin.write(payload)
            process.stdin.close()
        except OSError:
            pass  # container already gone; the wait path handles it

    @staticmethod
    def _ensure_image_available(image: str) -> None:
        """Fail fast (and outside the wall clock) if the image must be pulled."""
        try:
            probe = subprocess.run(  # noqa: S603 — fixed argv
                ["docker", "image", "inspect", image],
                capture_output=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RunnerUnavailableError(
                "Could not query Docker. Is the Docker engine running?"
            ) from exc

        if probe.returncode != 0:
            raise RunnerUnavailableError(
                f"Runner image '{image}' is missing. Run: docker pull {image}"
            )

    @staticmethod
    def _force_remove(container_name: str) -> None:
        try:
            subprocess.run(  # noqa: S603 — fixed argv, no shell
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):  # best effort only
            pass


def get_runner() -> DockerPythonRunner:
    """FastAPI dependency; override in tests with a fake runner."""
    return _runner_singleton


_runner_singleton = DockerPythonRunner()
