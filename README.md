# PyNivo

**Python, ready when you are.**

PyNivo is an offline-first desktop IDE designed to remove the initial setup barrier for
people learning Python. The current repository contains the Phase 1 editor foundation,
not a production IDE or bundled Python distribution yet.

## Current state

- Multi-tab Python editor with line numbers, highlighting, automatic indentation, current-line
  highlighting, horizontal/vertical scrolling, undo/redo, and conventional editing shortcuts.
- New, Open, Save, and Save As workflows with UTF-8 handling, atomic writes, dirty indicators,
  unsaved-change prompts, `.py` filtering, and recent files.
- Configurable editor font size and persisted window geometry.
- Separate-process Python execution with streamed stdout/stderr, keyboard input for `input()`,
  exit status, duplicate-run prevention, and Stop with a forced-kill fallback.
- Integrated output panel with visually distinct errors and a clear action.
- First-run welcome actions and an offline library of editable beginner examples.
- Deterministic parsing and beginner-friendly explanations for common Python tracebacks while
  keeping the complete original traceback visible.
- Structured offline lessons with explanations, runnable code, challenges, concepts, and hints.
- A complete 18-lesson beginner course covering Python fundamentals through files, exceptions,
  classes, testing, and a final project.
- Persistent cinematic dark and high-contrast light themes with a branded navigation rail and
  theme-aware editor, syntax, console, dialogs, and controls.
- Bundled-runtime discovery and validation compatible with an official Windows CPython embeddable
  distribution, with development-interpreter fallback when no bundle is present.
- Runtime abstraction that discovers and validates a development Python interpreter without
  hardcoding machine-specific paths.
- Safe execution-request construction using an executable and an argument list (never a shell
  command string).
- Rotating application logs that do not include learner source code.
- Unit tests for file operations, runtime discovery, validation, and execution requests.

Runtime binaries are not stored in Git or downloaded at startup. Development runs use the
interpreter that starts PyNivo until a verified runtime is staged for a production build.

## Development setup

Python 3.11 or newer is required for development. End users will not require a separate Python
installation once the bundled-runtime milestone is complete.

In Git Bash on Windows:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the application:

```bash
pynivo
```

Or run it as a module:

```bash
python -m pynivo
```

Run quality checks:

```bash
ruff check .
ruff format --check .
pytest
```

## Architecture

```text
src/pynivo/
├── app.py                 # application lifecycle and logging startup
├── ui/main_window.py      # Qt main-window shell
└── core/
    ├── execution/         # validated process launch descriptions
    ├── files/             # UTF-8 loading and atomic saving
    └── runtime/           # runtime discovery and validation
```

Learner programs must always run in a separate child process. This separation protects the GUI's
responsiveness, but it is **not a security sandbox**: Python programs can still access resources
available to the user's account.

## Dependency and licensing note

The runtime UI dependency is Qt for Python (PySide6). PySide6 is offered under LGPLv3/GPLv3 and
commercial terms. Before distributing PyNivo, the project must document and satisfy the applicable
Qt, CPython, and bundled third-party notice and redistribution requirements. No paid service,
account, telemetry SDK, or network backend is required.

The PyNivo project's own license has not yet been selected. Contributions should wait for that
decision and for a `CONTRIBUTING.md` policy in a later foundation step.

## Roadmap

Development follows the staged roadmap: editor, execution, beginner experience, error intelligence,
learning content, bundled runtime, and finally Windows distribution. The immediate next milestone is
user approval of the refreshed interface and course, followed by Windows packaging.
