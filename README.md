# PyNivo

**Python, ready when you are.**

PyNivo is an offline-first desktop IDE designed to remove the initial setup barrier for
people learning Python. The current repository contains the Phase 0 application foundation,
not a production IDE or bundled Python distribution yet.

## Current state

- Launchable PySide6 main-window shell with a simple beginner-oriented welcome screen.
- Runtime abstraction that discovers and validates a development Python interpreter without
  hardcoding machine-specific paths.
- Safe execution-request construction using an executable and an argument list (never a shell
  command string).
- Rotating application logs that do not include learner source code.
- Unit tests for runtime discovery, validation, and execution requests.

Editing, file management, child-process execution, lessons, and the bundled Windows runtime are
planned roadmap work and are not implemented in this bootstrap.

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
the editor and safe file lifecycle.

