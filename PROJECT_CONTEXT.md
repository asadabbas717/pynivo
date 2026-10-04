# Project Context

## Engineering audit update — 2026-10-05

Baseline for this audit: `1ce8b7f`, clean working tree. See
[ENGINEERING_AUDIT.md](ENGINEERING_AUDIT.md) for findings, scorecards, and limitations.
The following 2026-10-01 assessment is retained as a historical snapshot; this update
supersedes its resolved-defect and testing statements.

Fixed diagnostic stderr bounds (250,000-character tail), recovery JSON shape/path
validation, per-run Stop callback identity, split UTF-8 decoding, frozen builds falling
back to their GUI executable, and imported/edited-source error navigation. Untouched
starter tabs are now dirty and recoverable. Canceling window close preserves execution;
recovery-clear errors on accepted close are logged. Atomic-save replacement failure is
covered by a regression. Release tags are passed as environment data and both release
paths specify checkout SHA; PFX/P12 are ignored. CI checks dependency consistency and
builds wheels. Removed duplicate Hatchling forced inclusion after reproducing a wheel
build failure; wheel curriculum resources were verified in an isolated interpreter.

Local Python 3.13.15: 70 tests passed, one excluded; Ruff, pip consistency and wheel results are recorded
in the audit. Full pytest still blocks inside `QProcess.start()` for an invalid executable;
faulthandler localized the stall, but did not establish a root cause. The case remains
in the suite and CI. No frozen installer, signing, clean-machine, or manual theme QA
was completed. MainWindow remains the UI coordinator; no framework/dependency rewrite.


Repository assessment: 2026-10-01. Baseline: `main` at `8f5a3a4`; working tree
was clean before this documentation session. This is a dated snapshot, not a
live release/CI status report.

## Project overview

PyNivo is an offline-first desktop IDE for people learning Python. It combines a
multi-tab editor, separate-process execution with input/output, beginner error
guidance, editable examples, and an 18-lesson course. Windows builds bundle a
private interpreter so learners need no separate Python installation.

## Current project status

Active development / 0.1.0 prerelease preview. Editor, learning, runtime bundling,
and Windows distribution automation exist. Repository files describe an unsigned
preview and planned trusted signing; they do not establish that a release has
actually been published, signing credentials configured, or clean-machine QA
completed. There is no evidence of an active partial migration or assigned task;
recent work focuses on distribution, licensing, and onboarding.

## Technology stack

- Python >=3.11; source and packaging version 0.1.0.
- PySide6 ==6.11.2 for Qt widgets, settings, and asynchronous QProcess execution.
- Python standard library for files, JSON, subprocess validation, and analysis.
- Hatchling >=1.27 package build backend; pip for development installation.
- pytest >=8.3,<10; Ruff >=0.9,<1; PyInstaller >=6.20,<7 in development extras.
- Windows x64 CPython 3.13.15 embeddable runtime pinned by build URL and checksum.
- Inno Setup 7 recommended, with discovery of the standard Inno Setup 6 path.
- GitHub Actions: Windows quality matrix for Python 3.11/3.13, preview artifacts,
  and manual unsigned/signed draft prereleases.
- No database/ORM, web frontend/backend, HTTP API, authentication, or cloud storage.

## Current architecture summary

`app.py` initializes Qt and logging; `MainWindow` coordinates widgets, document
services, recovery, runtime discovery, and one `ProcessRunner`. Framework-free
core modules hold file/runtime/execution/error logic. Offline learning is bundled
JSON plus models. Preferences/course completion use QSettings, and recovery uses
local JSON. See [architecture](docs/architecture.md) for workflows and boundaries.

## Implemented features

Confirmed in code (implementation exists; this is not a production-quality claim):

- Multi-tab `.py` editing, syntax highlighting, indentation, line numbers,
  bracket matching, find/replace, dirty indicators, and save/close prompts.
- UTF-8/BOM reads, atomic same-folder saves, ten recent existing files, font and
  geometry preferences, persistent dark/light themes.
- One learner process at a time, stdout/stderr, stdin for `input()`, exit status,
  Stop followed by a two-second kill fallback, and run-source tracking across tabs.
- Deterministic traceback explanations and NameError spelling suggestions;
  analysis returns no result for unsupported non-traceback output.
- Version-aware welcome, examples, 18 ordered lessons, hints, editable starter
  code, and persisted manually marked completion.
- Unsaved-document recovery snapshots every 15 seconds, startup restore prompt,
  bounded visible output, and rotating application logs.
- Bundled-runtime preference/validation, development-interpreter fallback, and
  verified portable build plus per-user installer automation.
- Apache-2.0 project license and bundled third-party/LGPL compliance materials.

Partial/limited: traceback analysis is heuristic, recovery covers modified
documents only, and course completion has no automatic challenge checking.
Experimental/preview: Windows distributions are explicitly prerelease; trusted
signing depends on separately supplied credentials.

## Current work / in progress

Latest commits establish separate unsigned and signed prerelease paths, licensing
compliance, and cross-platform license hash consistency. No TODO/FIXME backlog,
unfinished feature branch, or author-assigned next task was found in inspected
tracked source. Signing and release validation remain continuity concerns, not
claims of work actively assigned to someone. Recommendations are in
[roadmap](docs/roadmap.md).

## Known problems and technical debt

- `MainWindow.program_error_output` grows `stderr_buffer` without a limit even
  though visible output is capped at 250,000 characters; noisy stderr can consume
  memory. Truncation also means the UI cannot retain every original traceback.
- Recovery JSON contains source code in plaintext. `RecoveryService.load` assumes
  a mapping after JSON parsing: syntactically valid JSON with an unexpected root
  shape can raise an uncaught AttributeError. Tests cover invalid JSON, not all
  valid-but-malformed structures.
- Recovery restores only modified documents, not a full saved-tab session, and
  changes since the last 15-second snapshot can be lost after a crash.
- `DocumentEditor` initially marks supplied starter code unmodified, so an
  untouched example/lesson tab is not a recovery snapshot candidate.
- Process Stop targets the direct child, not a managed descendant process tree.
  The delayed kill callback checks current process state rather than a run ID;
  regression coverage should examine rapid stop/restart. These are code-derived
  risks, not reproduced failures in this documentation session.
- Error navigation uses the last traceback line number in the original script's
  editor without validating the traceback filename; imported-file failures may
  navigate to an unrelated source line.
- Bracket matching/highlighting is text-based (not syntax-aware) and scans the
  full document on cursor changes; bracket selection colors remain hardcoded.
- The full-suite invalid-executable integration case stalled during this session;
  its cause remains unknown. The other 41 tests passed when it was excluded.
- Main-window/dialog workflows and installed clean-machine behavior lack an
  automated end-to-end suite. Content tests compile snippets, not execute every
  lesson. Packaging download/extraction/smoke functions lack direct unit coverage.
- No package manager is implemented. Bundled Python excludes pip/Tk/docs; its
  isolation configuration must be preserved. Missing bundles in frozen builds
  can fall back to the application executable, which is not a learner Python
  interpreter; `--skip-runtime` is diagnostics-only.
- Versions are repeated across package metadata, Python module, Windows resource,
  installer, and preview documentation; coordinate updates.

## Important constraints and decisions

Offline-first, no startup binary downloads, no accounts/telemetry/paid services,
and child-process execution are established project expectations. Child processes
are not a security sandbox. Windows installer targets Windows >=10 and x64
compatible systems with per-user privileges; other platforms have no distribution
pipeline. New core logic should remain independent of Qt.

See [decisions](docs/decisions.md) for evidence and implications, including atomic
saves, QSettings, private runtime, and distinct release paths. Original decision
rationales are only recorded where existing documentation supports them.

## Environment variables

No application `.env` template or required user-supplied secrets exist.
Variable names only:

| Variable | Use |
| --- | --- |
| `PYTHONIOENCODING`, `PYTHONUTF8` | Set by ProcessRunner for learner-process UTF-8 I/O |
| `LOCALAPPDATA` | Overridden during packaged smoke testing to redirect app data |
| `GH_TOKEN` | GitHub workflow release creation using the workflow token |
| `WINDOWS_SIGNING_CERTIFICATE_BASE64`, `WINDOWS_SIGNING_CERTIFICATE_PASSWORD` | GitHub Actions signing secrets |
| `SIGNING_CERTIFICATE`, `SIGNING_PASSWORD` | Workflow environment aliases of those secrets |
| `RUNNER_TEMP` | Workflow temporary signing certificate location |

## How to run

From repository root, PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m pynivo
```

No server, database setup, or environment file is needed. With an activated
environment, `pynivo` or `python -m pynivo` launches the GUI. `--welcome` forces
onboarding; `--smoke-test` launches briefly without onboarding/recovery restore
and without normal file logging. It is not an exhaustive or fully side-effect-free
test: MainWindow still creates its settings and recovery timer.

## Testing status

pytest contains 42 tests under `tests/unit` and `tests/integration`. Unit coverage
includes files/recovery, runtime, execution requests, output limits, curriculum,
progress, errors, editing helpers, themes, onboarding, notices, and installer text.
Integration tests run real QProcess children for Unicode channels, input, stop,
duplicate prevention, and launch failures, using a Qt core event loop.

```powershell
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
```

Local validation on 2026-10-01 (Python 3.13.15): Ruff lint passed; format check
passed (73 files); `git diff --check` passed. Full pytest stalled after the first
four integration cases at the invalid-executable case and was interrupted; no
cause was established. Rerun with `-k 'not unlaunchable_executable'` passed all
41 selected tests (one deselected). Treat the full suite as unverified, not passed.
Windows portable/installer builds were not rerun for this documentation-only change. CI defines
Windows Python 3.11 and 3.13 checks; CI configuration alone does not prove a run
passed. See known problems for gaps.

## Deployment status

Desktop distribution, not web deployment. `packaging/windows/build.py` uses
PyInstaller onedir, downloads/checksums/extracts private CPython at build time,
copies compliance files, and smoke-tests the learner runtime and executable.
`build_installer.py` invokes Inno Setup and produces `dist/installer/` output.
The per-user installer launches the app with `--welcome` after interactive setup.

```powershell
.venv/Scripts/python.exe packaging/windows/build.py
.venv/Scripts/python.exe packaging/windows/build_installer.py --skip-portable
```

Use `--skip-portable` only after a verified portable build; it does not itself
revalidate the reused directory. Build prerequisites and all workflows are in
[architecture](docs/architecture.md). Preview workflow uploads expire after 14
days. Both release workflows create drafts; this session does not publish them.
Signed release requires secrets and SignTool verification; unsigned preview
requires an explicitly unsigned installer and preview-tag format. No live release
availability, certificate readiness, or production support was independently verified.

## Lightweight security review

Tracked-file name/content review found no credential-like literal or tracked
environment/private-key/certificate file requiring disclosure. This is a heuristic
review of current tracked files, not a complete historical secret audit.
`.gitignore` excludes environment files except `.env.example`, PEM/KEY files,
local runtime binaries, logs, recovery, environments, and generated builds. It
does not explicitly exclude PFX/P12 or generic service-account JSON; adding those
patterns is a recommended follow-up. No credentials were copied into this handoff.

Learner processes inherit the system environment and can access user resources,
including environment credentials. Recovery and console input can contain private
text; never upload them as routine diagnostics. Signed certificate material is
written to runner temporary storage and removed in an always-run cleanup step.
Manual workflow tag inputs are embedded directly in PowerShell source; consider
passing them as environment variables before accepting untrusted dispatch inputs.

## Recent important changes

Git history, not inferred publication history:

- `46f4276`: recovery and bounded visible output.
- `ae3d9d7`, `5f13080`: editor tools and associating run results with source document.
- `450e56a`, `a8981cb`, `82fdb17`: verified Windows build/release checks and Inno 6 discovery.
- `dcb4897`, `9040d5b`: installed ownership/license display and explicit welcome launch.
- `ddcd5f6`: LGPL compliance materials and credential-gated signed prerelease.
- `da369cb`: separate unsigned preview publishing path.
- `8f5a3a4`: normalize license hash testing across platforms, with license LF policy.

These latest release-related commits are dated 2026-09-23/24. This session adds
continuity documents and corrects outdated foundation/future-tense descriptions;
application behavior is unchanged.

## Recommended next steps

1. Harden stderr limits and recovery schema handling with regression tests.
2. Add main-window execution/navigation and stop/restart tests for the identified risks.
3. Validate installation, onboarding, stdin/output, stop, recovery, and both themes
   on a clean Windows 10/11 machine; record actual results and artifacts.
4. Close release-input/credential-ignore gaps, establish private security reporting,
   and configure trusted signing when available.
5. Expand packaging tests and coordinate repeated version metadata before a release.

# Session Handoff

## What the next developer/agent should read first

1. `AGENTS.md`
2. `PROJECT_CONTEXT.md`
3. `docs/architecture.md`
4. `docs/decisions.md`
5. `docs/roadmap.md`

## Before continuing development

```bash
git status
git log --oneline -10
```

Then run the pytest/Ruff commands above using the chosen development interpreter.
Run Windows build checks when packaging changes warrant them.

## Current handoff summary

The 0.1.0 desktop preview has editor, offline course, execution, recovery, themes,
and Windows distribution code. Recent significant work is release/licensing and
onboarding, followed by this documentation-only context preservation session.
The most immediate code concern is unbounded diagnostic stderr; next address that
and malformed recovery data with tests. The major warning is that learner code
has normal user privileges and inherited environment access: process separation
does not sandbox it. Signing and published-release status remain unverified.
