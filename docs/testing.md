# Testing and validation

From the repository root in PowerShell, install `.[dev]` and run:

```powershell
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m pip wheel . --no-deps --wheel-dir build/wheels
git diff --check
```

Tests retain one offscreen QApplication in `tests/conftest.py`. MainWindow tests
redirect QSettings and recovery to temporary paths; they do not touch learner state.
Core tests protect atomic saves, recovery schemas, runtime validation, bounded output,
error analysis, curriculum identity/order, and licensing. Integration tests use real
QProcess children for output/input, stop, duplicate rejection, and split UTF-8.
The stale Stop callback test simulates a previous generation while a real new process
runs; it does not exercise all real timer scheduling or descendant processes.
Packaging tests validate bad checksums, archive traversal, and missing artifacts.

## Known local blocker

On 2026-10-05, Python 3.13.15/PySide6 6.11.2 blocked inside `QProcess.start()` in
`test_runner_reports_unlaunchable_executable`, reproducing the earlier handoff stall.
Faulthandler localized the call; the underlying Qt/Windows/environment cause remains
unknown. The event-loop timer cannot interrupt that synchronous call. The test is
retained, and CI does not exclude it. A diagnostic subset can be run with:

```powershell
.venv/Scripts/python.exe -m pytest -k 'not unlaunchable_executable'
```

The final selected run passed 70 tests with one deselected.
This is a partial-suite result, never evidence of a full-suite pass. See the audit for
actual results. Build and inspect a wheel separately: editable installation cannot
catch duplicate inclusion or missing resources. Local audit loaded both JSON libraries
from the built wheel in Python isolated mode.

## Release validation still required

Run the portable/installer commands documented in architecture on a configured Windows
build machine. Record artifact version/checksum, signing status, and tested OS. On clean
Windows 10/11 verify install/uninstall, offline startup, welcome, Unicode editing/save,
stdin/output, Stop, recovery, dirty prompts, both themes, keyboard and screen-reader
navigation. GUI smoke tests and component checks do not replace this manual evidence.
