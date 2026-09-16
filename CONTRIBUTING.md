# Contributing to PyNivo

PyNivo is at an early foundation stage. Keep changes focused on the current roadmap milestone and
preserve the beginner-first, offline-first product direction.

## Local setup

Use Python 3.11 or newer. From Git Bash on Windows:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Before submitting a change, run:

```bash
ruff check .
ruff format --check .
pytest
```

## Design expectations

- Learner programs must never execute inside the GUI process.
- Do not add network services, telemetry, accounts, or paid dependencies to the core application.
- Keep Qt code in the UI or process-adapter layer; keep business models and validation testable
  without a GUI.
- Do not log learner source code or secrets.
- Add tests for behavior and update documentation when user-visible behavior changes.

The project license is not yet selected, so contribution and redistribution terms must be resolved
before accepting external contributions or publishing a release.

