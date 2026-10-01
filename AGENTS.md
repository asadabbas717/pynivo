# Agent instructions

## Project identity

PyNivo 0.1.0 is a beginner-focused, offline-first Python desktop IDE. It removes
setup friction through an editor, offline curriculum, and a private learner
interpreter in Windows distributions. It uses Python >=3.11, PySide6 6.11.2,
pytest, Ruff, Hatchling, PyInstaller, and Inno Setup. It has no web backend,
database server, accounts, or telemetry.

## Before making changes

1. Read this file and `PROJECT_CONTEXT.md`.
2. Read relevant sections of `docs/architecture.md`, `docs/decisions.md`, and
   `docs/roadmap.md`.
3. Run `git status` and inspect recent history.
4. Inspect related implementation and tests, particularly all callers before
   changing shared logic. Understand current behavior before editing.

## Operating rules

- Preserve the established architecture; avoid unnecessary rewrites, duplicate
  code, and dependencies. Prefer readable, maintainable changes and reasonable
  backward compatibility. Explain significant architectural changes.
- Keep core models, file services, runtime validation, text helpers, and learning
  models independent of Qt. Qt belongs in UI and the process adapter.
- Learner code must execute only in a child process. Never import or execute it
  inside the GUI. Preserve executable/argument-list launches without a shell.
- Preserve the identity and source snapshot of the running document even if the
  selected tab changes. Consult `MainWindow.run_current_document` and completion
  handlers together.
- Preserve atomic UTF-8 source saves, dirty-state prompts, and local recovery.
  Recovery contains learner source: never commit, upload, or log it.
- Keep the application offline-first: no startup executable downloads, accounts,
  telemetry, paid dependencies, or network backend in the core application.
- Use shared theme palettes/QSS for new screens and dialogs; manually review
  both themes. Existing bracket-highlight colors are an exception to clean up,
  not a pattern to extend.
- Preserve stable lesson identifiers and curriculum order: persisted completion
  uses those identifiers. Bundled JSON must remain included in wheels and frozen
  builds. Completion is learner-reported, not automated grading.
- Never commit secrets or hardcode credentials. Preserve environment-based CI
  signing credentials. Do not print secret values during repository inspection.
- Keep runtime binaries, build artifacts, virtual environments, recovery, logs,
  and signing certificates out of Git. Do not change canonical license texts;
  `.gitattributes` and compliance tests protect their cross-platform hashes.
- Preserve the unsigned-preview disclosures and signed-release credential gate.
  Keep Apache and dependency notices in distributions. Review all version
  locations when preparing a version bump (see `docs/architecture.md`).
- Follow existing snake_case names, type annotations, and dataclass patterns.
  Ruff targets Python 3.11, uses 100-character lines and double quotes, and
  selects E/F/I/UP/B/SIM rules. Qt event overrides retain Qt names with existing
  targeted noqa comments.

## Development environment and commands

From repository root in PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m pynivo
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
```

Use `python -m ...` with an activated environment on other shells/platforms.
Format with `.venv/Scripts/python.exe -m ruff format .` when needed.
Windows portable build: `.venv/Scripts/python.exe packaging/windows/build.py`.
Windows installer: `.venv/Scripts/python.exe packaging/windows/build_installer.py`
(requires Inno Setup; release CI uses Python 3.13). Build/runtime details and
diagnostic-only flags are in `docs/architecture.md`. No web dev server exists.

## Repository navigation

| Path | Responsibility |
| --- | --- |
| `src/pynivo/app.py`, `__main__.py`, `paths.py` | Startup, logging, source/frozen paths |
| `src/pynivo/ui/main_window.py` | Documents, execution orchestration, settings, recovery |
| `src/pynivo/ui/editor/`, `console/`, `dialogs/`, `themes.py` | Widgets, editing, output, learning UI, palette |
| `src/pynivo/core/files/`, `runtime/`, `execution/`, `errors/` | Pure services, validation, bounded output, traceback analysis |
| `src/pynivo/services/process_runner.py` | Qt child-process adapter |
| `src/pynivo/learning/` | Curriculum models, progress, bundled JSON |
| `tests/unit/`, `tests/integration/` | Pure/component tests and real QProcess tests |
| `packaging/windows/`, `packaging/runtime/` | Frozen build, installer, private-runtime guidance |
| `pyproject.toml`, `.github/workflows/` | Dependencies, quality checks, release automation |

## After making changes

1. Run relevant tests and available lint/format/build checks appropriate to scope.
2. Inspect `git diff` and ensure no secrets or generated artifacts were introduced.
3. Update documentation when behavior or architecture changes.
4. Update `PROJECT_CONTEXT.md` when status changes, `docs/decisions.md` for
   significant decisions, and `docs/roadmap.md` for completed or added work.
5. Report checks actually run and distinguish local results from CI/release
   verification. Do not claim production readiness or a published release from
   configuration alone.
