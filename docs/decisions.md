# Technical Decisions

Evidence-based current choices, assessed 2026-10-01 at `8f5a3a4`. These are
retrospective records; unrecorded historical rationale is not invented.

## Decision 001 — Offline-first native Qt desktop IDE

**Status:** Current

**Context:** README/CONTRIBUTING establish beginner setup friction and offline use
as goals. Original framework-selection rationale is not recorded.

**Decision:** Python/PySide6 widgets with no account, telemetry, paid service, or
network backend in the core application.

**Evidence:** `pyproject.toml`, `app.py`, `ui/main_window.py`, `CONTRIBUTING.md`.

**Consequences:** No service credentials needed locally; GUI distribution/QA
remain platform-specific and builds still fetch dependencies/runtime.

## Decision 002 — Qt-independent core and child-process execution

**Status:** Current

**Context:** Existing architecture documentation prioritizes testability and GUI
responsiveness.

**Decision:** Pure core services/models plus a QProcess adapter consuming an
executable/argument-list ExecutionRequest. Learner code never enters the GUI.

**Evidence:** `core/`, `services/process_runner.py`, process integration tests.

**Consequences:** Fast core tests and asynchronous interaction. One program at a
time; normal user/environment access remains. This is not a security sandbox.

## Decision 003 — Atomic UTF-8 saves and local crash recovery

**Status:** Current

**Context:** `46f4276` adds recovery. Original detailed rationale is not recorded;
implementation protects source replacement and retains modified buffers.

**Decision:** Temporary sibling plus fsync/os.replace for source saves and a
separate versioned recovery JSON snapshot every 15 seconds.

**Evidence:** `core/files/`, MainWindow snapshot/restore/close handlers, file tests.

**Consequences:** Recovery does not directly overwrite source; it is plaintext,
periodic, limited to modified buffers, and needs further schema validation.

## Decision 004 — Bundled curriculum and QSettings progress

**Status:** Current

**Context:** Learning milestones include `3d98147`. Original storage-selection
rationale is not recorded.

**Decision:** JSON examples/lessons with immutable models; QSettings for stable-ID
completion, preferences, recent files, and version-aware welcome.

**Evidence:** `learning/`, `ui/dialogs/lessons_dialog.py`, `ui/onboarding.py`,
resource inclusion in `pyproject.toml` and `pynivo.spec`.

**Consequences:** No database/service needed. Preserve lesson IDs/order and resource
packaging. Completion is manually marked; dialog drafts are not persisted.

## Decision 005 — Local guidance tied to original run source

**Status:** Current

**Context:** `ea7847b` and `5f13080` improve guidance and preserve results across tab
changes.

**Decision:** Regex traceback analysis and deterministic explanations/suggestions;
capture source/path before running rather than use the selected tab on completion.

**Evidence:** `core/errors/analyzer.py`, MainWindow run/completion handlers.

**Consequences:** No external AI API. Analysis is heuristic; filename validation
and stderr memory bounds remain follow-ups. Visible output can be truncated.

## Decision 006 — Private interpreter and Windows onedir distribution

**Status:** Current

**Context:** Beginner setup goals and `450e56a` support self-contained Windows use.

**Decision:** PyInstaller onedir GUI, pinned/checksummed official CPython embeddable
runtime, and Inno per-user installer. No startup executable downloads.

**Evidence:** Windows build/spec/installer files, `core/runtime/manager.py`,
`packaging/runtime/README.md`.

**Consequences:** No separate learner Python/admin install; bundled isolation
excludes pip/Tk/docs. Packages need a designed future strategy. Windows is the
only configured distribution target.

## Decision 007 — Apache project license and preserved LGPL dependencies

**Status:** Current

**Context:** `176d0d6`, `9040d5b`, `ddcd5f6` establish attribution/licensing and
compliance materials; `8f5a3a4` addresses cross-platform hashes.

**Decision:** Apache-2.0 project code; dynamically loaded unmodified Qt/PySide6
retain their licenses. Include notices, texts, exact source references, and
replacement instructions; canonical license files use LF.

**Evidence:** LICENSE/NOTICE, third-party and Qt compliance docs, `.gitattributes`,
license tests, build copy steps.

**Consequences:** Preserve upstream texts and update references when dependencies
change. Project license does not relicense bundled components. This records
repository policy, not a new legal assessment.

## Decision 008 — Separate unsigned and signed prerelease workflows

**Status:** Current

**Context:** `ddcd5f6` gates signed releases; `da369cb` adds disclosed unsigned
previews pending trusted signing.

**Decision:** Manual draft prereleases with checksums. Signed path requires secrets
and SignTool verification; unsigned path requires preview tags and NotSigned
status, with explicit disclosures.

**Evidence:** `.github/workflows/release.yml`, `unsigned-preview-release.yml`,
`CODE_SIGNING.md`, `UNSIGNED_PREVIEW.md`.

**Consequences:** Draft creation is not publication; unsigned checksums do not
establish publisher trust. Credential readiness/live release state is unverified.
Review dispatch input handling and tag targeting before subsequent releases.

## Decision 009 — Bounded diagnostics and execution identity guards

**Status:** Current engineering decision, 2026-10-05.

**Context:** Unbounded stderr and delayed Stop callbacks could exhaust memory or
terminate a subsequent run. Per-read UTF-8 decoding corrupted split characters;
tracebacks from imports or an older source snapshot could navigate incorrectly.

**Decision:** Retain a 250,000-character stderr tail, use per-channel incremental
decoders, bind delayed kills to the run generation/stopping state, and navigate only
to a matching file and unchanged source snapshot with a valid line number.

**Alternatives:** Retain all output on disk, create a new process adapter per run,
or rewrite execution into a general task framework.

**Rationale/trade-offs:** Small guards preserve the existing asynchronous adapter
and protect concrete failures without dependencies. Earlier diagnostics can be lost;
process descendants remain outside the Stop contract. Source matching is conservative.

## Decision 010 — Validate recovery and distributable artifacts at their boundaries

**Status:** Current engineering decision, 2026-10-05.

**Context:** Recovery accepts external local JSON; editable installs concealed duplicate
wheel inclusion. Frozen GUI executables must never become learner interpreters.

**Decision:** Reject invalid snapshot roots/containers and invalid entry paths while
retaining valid entries. Keep version-1 data compatibility. Untitled nonempty starter
buffers are dirty. Frozen runs require the private runtime. Use normal package resource
inclusion and build wheels in CI, in addition to source tests and `pip check`.

**Alternatives:** Migrate recovery to a database or introduce schema/dependency tooling.

**Rationale/trade-offs:** Existing dataclasses, JSON, and package layout suffice.
No migration or new runtime dependency is needed. This does not establish full session
persistence, locked toolchains, or installed-machine QA.
