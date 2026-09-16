from pathlib import Path

import pytest

from pynivo.core.runtime import BundledRuntimeManager, RuntimeResolver
from pynivo.core.runtime.manager import RuntimeValidationError


def test_bundled_runtime_is_preferred_when_present(tmp_path: Path) -> None:
    executable = tmp_path / "runtime" / "python.exe"
    executable.parent.mkdir()
    executable.touch()

    assert RuntimeResolver(tmp_path).locate_runtime() == executable


def test_bundled_runtime_requires_complete_layout(tmp_path: Path) -> None:
    executable = tmp_path / "runtime" / "python.exe"
    executable.parent.mkdir()
    executable.touch()

    with pytest.raises(RuntimeValidationError, match="standard library"):
        BundledRuntimeManager(tmp_path).validate_runtime(executable)


def test_missing_bundle_falls_back_to_development_runtime(tmp_path: Path) -> None:
    runtime = RuntimeResolver(tmp_path).locate_runtime()

    assert runtime is not None
    assert runtime.is_file()
