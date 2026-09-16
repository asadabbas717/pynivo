from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from pynivo.core.execution import ExecutionRequest
from pynivo.services import ProcessRunner


def application() -> QCoreApplication:
    return QCoreApplication.instance() or QCoreApplication([])


def run_and_wait(
    runner: ProcessRunner, request: ExecutionRequest, timeout_ms: int = 5000
) -> tuple[int, bool]:
    app = application()
    loop = QEventLoop()
    result: list[tuple[int, bool]] = []
    runner.finished.connect(lambda code, stopped: (result.append((code, stopped)), loop.quit()))
    QTimer.singleShot(timeout_ms, loop.quit)
    assert runner.run(request)
    loop.exec()
    app.processEvents()
    assert result, "process did not finish before timeout"
    return result[0]


def test_runner_captures_unicode_stdout_and_stderr(tmp_path: Path) -> None:
    script = tmp_path / "unicode output.py"
    script.write_text(
        "import sys\nprint('سلام')\nprint('problem', file=sys.stderr)\n", encoding="utf-8"
    )
    runner = ProcessRunner()
    output: list[str] = []
    errors: list[str] = []
    runner.output_received.connect(output.append)
    runner.error_received.connect(errors.append)

    exit_code, stopped = run_and_wait(
        runner, ExecutionRequest.for_script(Path(sys.executable), script)
    )

    assert exit_code == 0
    assert not stopped
    assert "سلام" in "".join(output)
    assert "problem" in "".join(errors)


def test_runner_supports_standard_input(tmp_path: Path) -> None:
    script = tmp_path / "input.py"
    script.write_text("name = input()\nprint(f'Hello, {name}!')\n", encoding="utf-8")
    runner = ProcessRunner()
    output: list[str] = []
    runner.output_received.connect(output.append)
    runner.started.connect(lambda: runner.write_input("Ada"))

    exit_code, stopped = run_and_wait(
        runner, ExecutionRequest.for_script(Path(sys.executable), script)
    )

    assert (exit_code, stopped) == (0, False)
    assert "Hello, Ada!" in "".join(output)


def test_runner_stops_long_running_program(tmp_path: Path) -> None:
    script = tmp_path / "forever.py"
    script.write_text("while True:\n    pass\n", encoding="utf-8")
    runner = ProcessRunner()
    runner.started.connect(lambda: QTimer.singleShot(100, runner.stop))

    _exit_code, stopped = run_and_wait(
        runner, ExecutionRequest.for_script(Path(sys.executable), script)
    )

    assert stopped
