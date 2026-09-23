# PyNivo

**Python, ready when you are.**

PyNivo is an offline-first desktop IDE designed to remove the initial setup barrier for people
learning Python. The repository now contains the complete pre-release editor, learning experience,
execution system, and a reproducible Windows portable-build pipeline.

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
- Persistent course progress, completed-lesson indicators, previous/next navigation, editable
  starter code, reset controls, challenges, and contextual hints.
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

## Windows portable build

Install the development dependencies, then run this command from Git Bash on 64-bit Windows:

```bash
python packaging/windows/build.py
```

The build downloads the pinned official CPython embeddable runtime into the ignored build cache,
verifies its published SHA-256 checksum, creates `dist/PyNivo/PyNivo.exe`, and smoke-tests both the
application and private learner runtime. End-user startup never downloads executable components.

The generated `dist/` directory is a local preview artifact and is not committed to Git. Automated
workflows can create either a clearly disclosed unsigned preview or a certificate-gated signed
prerelease. Compliance files and checksums are included in both distributions.

After installing Inno Setup 7, create a non-administrator, per-user preview installer with:

```bash
python packaging/windows/build_installer.py --skip-portable
```

### Unsigned Windows preview

The current GitHub preview installer is not digitally signed. Windows may identify the publisher
as **Unknown publisher** or display **Windows protected your PC**. Download it only from the official
PyNivo GitHub release page and compare the installer SHA-256 value with `SHA256SUMS.txt`. See
[UNSIGNED_PREVIEW.md](UNSIGNED_PREVIEW.md) for verification and installation guidance.

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

The runtime UI dependency is Qt for Python (PySide6), distributed with PyNivo under LGPLv3.
The release bundle includes the applicable license texts, corresponding-source information, and
library-replacement instructions. No paid service, account, telemetry SDK, or network backend is
required.

PyNivo is licensed under the Apache License 2.0. Copyright 2026 Asad Abbas. Bundled dependencies
remain subject to their respective licenses; see `THIRD_PARTY_NOTICES.md`.

## License

PyNivo is Copyright 2026 Asad Abbas and licensed under Apache License 2.0.
The Windows distribution includes unmodified Qt/PySide6 libraries under
LGPLv3; see [QT_LGPL_COMPLIANCE.md](QT_LGPL_COMPLIANCE.md) for the corresponding
source and library-replacement instructions.

PyNivo source code is available under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for
copyright attribution and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for bundled components.

## Roadmap

Development follows the staged roadmap: editor, execution, beginner experience, error intelligence,
learning content, bundled runtime, and Windows distribution. The current milestone is an unsigned
public preview; trusted code signing remains planned for a later release.
