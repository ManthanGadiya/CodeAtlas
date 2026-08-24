"""End-to-end execution tests against REAL Docker containers.

Skipped automatically when the Docker engine is unavailable (CI without
Docker, or Docker Desktop not started locally). Run explicitly with:

    pytest -m docker
"""

import shutil
import subprocess

import pytest

from app.problems.seed import seed_problems

pytestmark = [
    pytest.mark.docker,
    pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI not installed"),
]

REGISTER = {"email": "student@example.com", "password": "correct-horse-battery"}


def _docker_engine_available() -> bool:
    try:
        probe = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return probe.returncode == 0


@pytest.fixture()
def engine_ready():
    if not _docker_engine_available():
        pytest.skip("Docker engine is not running")
    yield


@pytest.fixture()
def seeded_client(client, db_session):
    seed_problems(db_session)
    client.post("/api/auth/register", json=REGISTER)
    return client


TWO_SUM_SOLUTION = (
    "def two_sum(nums, target):\n"
    "    seen = {}\n"
    "    for i, value in enumerate(nums):\n"
    "        if target - value in seen:\n"
    "            return [seen[target - value], i]\n"
    "        seen[value] = i\n"
)


def test_real_container_grades_correct_solution(seeded_client, engine_ready):
    response = seeded_client.post("/api/problems/two-sum/run", json={"code": TWO_SUM_SOLUTION})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["summary"] == {"passed": 3, "total": 3}


def test_real_container_kills_infinite_loop(seeded_client, engine_ready, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setenv("EXEC_TIMEOUT_SECONDS", "4")
    get_settings.cache_clear()
    try:
        response = seeded_client.post(
            "/api/problems/two-sum/run", json={"code": "while True:\n    pass\n"}
        )
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    assert response.json()["status"] == "TIMEOUT"


def test_real_container_enforces_memory_limit(seeded_client, engine_ready):
    response = seeded_client.post(
        "/api/problems/two-sum/run",
        json={"code": "x = bytearray(300_000_000)\ndef two_sum(nums, t):\n    return []\n"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "MEMORY_LIMIT"


def test_real_container_blocks_network(seeded_client, engine_ready):
    # IP literal on purpose: DNS resolution can hang well past the wall
    # clock on a network-less container, while connect() to a routable
    # address answers immediately (ENETUNREACH) or succeeds if networking
    # were ever wrongly enabled.
    solution = (
        "import socket\n"
        "def two_sum(nums, target):\n"
        "    try:\n"
        "        socket.create_connection(('1.1.1.1', 443), timeout=3)\n"
        "        return 'network-open'\n"
        "    except OSError:\n"
        "        return 'network-blocked'\n"
    )
    response = seeded_client.post("/api/problems/two-sum/run", json={"code": solution})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["results"][0]["actual_output"] == "network-blocked"


def test_real_container_has_read_only_filesystem(seeded_client, engine_ready):
    solution = (
        "def two_sum(nums, target):\n"
        "    try:\n"
        "        with open('/etc/passwd', 'a', encoding='utf-8') as handle:\n"
        "            handle.write('x')\n"
        "        return 'wrote'\n"
        "    except OSError:\n"
        "        return 'read-only'\n"
    )
    response = seeded_client.post("/api/problems/two-sum/run", json={"code": solution})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["results"][0]["actual_output"] == "read-only"
