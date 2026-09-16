from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pynivo.core.runtime.manager import RuntimeValidationError, SystemRuntimeManager


def test_locate_runtime_finds_current_interpreter() -> None:
    runtime = SystemRuntimeManager().locate_runtime()

    assert runtime is not None
    assert runtime.samefile(Path(sys.executable))


def test_validate_runtime_reports_python_version() -> None:
    manager = SystemRuntimeManager()

    info = manager.validate_runtime(Path(sys.executable))

    assert info.executable.samefile(Path(sys.executable))
    assert info.version.startswith(f"{sys.version_info.major}.{sys.version_info.minor}.")


def test_validate_runtime_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(RuntimeValidationError, match="not found"):
        SystemRuntimeManager().validate_runtime(tmp_path / "missing-python.exe")
