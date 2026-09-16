from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pynivo.core.execution import ExecutionRequest, ExecutionRequestError


def test_for_script_preserves_spaces_and_unicode_as_one_argument(tmp_path: Path) -> None:
    script = tmp_path / "my café program.py"
    script.write_text("print('hello')\n", encoding="utf-8")

    request = ExecutionRequest.for_script(Path(sys.executable), script)

    assert request.executable.samefile(Path(sys.executable))
    assert request.arguments == (str(script.resolve()),)
    assert request.working_directory == tmp_path.resolve()


def test_for_script_rejects_non_python_file(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("not Python", encoding="utf-8")

    with pytest.raises(ExecutionRequestError, match=r"\.py"):
        ExecutionRequest.for_script(Path(sys.executable), text_file)


def test_for_script_rejects_missing_script(tmp_path: Path) -> None:
    with pytest.raises(ExecutionRequestError, match="not found"):
        ExecutionRequest.for_script(Path(sys.executable), tmp_path / "missing.py")
