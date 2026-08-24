"""Unit tests for the docker command builder — CI's sandbox-flag tripwire.

The fake-runner API tests never see real argv; these tests make a broken
or weakened container configuration fail CI even without Docker installed.
"""

from app.core.config import Settings
from app.execution.runner import build_run_command


def _flags(command: list[str]) -> set[tuple]:
    """Collapse argv into flag pairs for assertion-friendly lookups."""
    pairs = set()
    for index, token in enumerate(command):
        if token.startswith("--"):
            value = (
                command[index + 1]
                if index + 1 < len(command) and not command[index + 1].startswith("--")
                else ""
            )
            pairs.add((token, value))
    return pairs


def test_security_critical_flags_are_present():
    settings = Settings(_env_file=None)
    command = build_run_command(settings, "codeatlas-exec-test")
    flags = _flags(command)

    assert ("--network", "none") in flags
    assert ("--read-only", "") in flags
    assert ("--cap-drop", "ALL") in flags
    assert ("--user", "65534:65534") in flags
    assert ("--pids-limit", str(settings.exec_pids_limit)) in flags
    assert ("--memory", f"{settings.exec_memory_mb}m") in flags
    assert ("--memory-swap", f"{settings.exec_memory_mb}m") in flags
    assert ("--init", "") in flags
    assert ("--security-opt", "no-new-privileges") in flags


def test_tmpfs_is_noexec_nosuid_nodev():
    settings = Settings(_env_file=None)
    command = build_run_command(settings, "codeatlas-exec-test")

    tmpfs_spec = next(value for flag, value in _flags(command) if flag == "--tmpfs")
    assert "noexec" in tmpfs_spec
    assert "nosuid" in tmpfs_spec
    assert "nodev" in tmpfs_spec


def test_harness_mount_is_read_only():
    from app.execution.runner import HARNESS_DIR

    settings = Settings(_env_file=None)
    command = build_run_command(settings, "codeatlas-exec-test")

    mount_index = command.index("--volume")
    mount_spec = command[mount_index + 1]
    assert mount_spec == f"{HARNESS_DIR}:/sandbox:ro"


def test_image_and_entrypoint_are_last():
    settings = Settings(_env_file=None)
    command = build_run_command(settings, "codeatlas-exec-test")

    assert command[-4] == settings.docker_image
    assert command[-3:] == ["python", "-S", "/sandbox/harness.py"]
