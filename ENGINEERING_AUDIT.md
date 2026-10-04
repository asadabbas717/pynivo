# Engineering Audit

Assessment date: 2026-10-05. Baseline: `1ce8b7f` (clean working tree).
Scope: tracked application/core/UI/learning modules, tests, packaging, workflows,
configuration, documentation, current Git inventory and recent history. This is a
source and local engineering assessment, not certification or a historical secret audit.

## Executive Summary

PyNivo began as a coherent, maintainable desktop preview with good offline boundaries,
child-process execution, atomic source saves, compliance materials, and candid handoff
documentation. Its main weaknesses were edge-case reliability and insufficient artifact
and UI workflow verification. The architecture does not justify a rewrite.

Incremental improvements fix malformed recovery crashes, unbounded diagnostic memory,
stale Stop callbacks, split UTF-8 corruption, misleading traceback navigation, lost
starter-buffer recovery, and frozen runtime fallback. A real wheel build uncovered and
reproduced duplicate resource inclusion; normal package inclusion now builds successfully.
Release inputs are data rather than executable PowerShell text. New behavioral regressions
and CI artifact/dependency checks improve confidence. The full local test suite remains
blocked by the pre-existing invalid-executable QProcess launch stall.

Overall judgment: **portfolio quality, with several senior engineering practices**.
This is still a prerelease, not demonstrated senior-engineered production quality.
No honest assessment can award 10/10 before unresolved launch, shutdown, installed-app,
accessibility, and release verification gaps are closed.

## Original Score

Scores are evidence-based judgments relative to a small offline desktop IDE, not objective
measurements. Overall is a rounded equal-category average; database design, authentication,
HTTP APIs and synchronization are N/A. Persistence scores local source/recovery/settings.

| Category | Original | Final |
| --- | ---: | ---: |
| Architecture | 8 | 8 |
| Code Quality | 7 | 7.5 |
| SOLID / Design | 8 | 8 |
| Domain Modeling | 7 | 8 |
| Security | 6 | 7 |
| Reliability | 5 | 7 |
| Testing | 6 | 7.5 |
| Database/Persistence | 6 | 8 |
| Performance | 6 | 6.5 |
| Configuration | 7 | 7.5 |
| Dependencies | 6 | 6 |
| Logging/Observability | 7 | 7 |
| UI/UX Robustness | 6 | 7 |
| Accessibility | 4 | 4 |
| Documentation | 8 | 8.5 |
| Developer Experience | 7 | 8 |
| CI/CD | 7 | 7.5 |
| Deployment/Release | 5 | 6 |
| Repository Hygiene | 8 | 8.5 |
| Overall | **6.5** | **7.2** |

Concurrency: improved run identity and decoding; descendant/shutdown ownership remains
incomplete. Integration/API design: the typed executable/argument-list request is appropriate;
remote API concerns are N/A. Git practices: recent history shows incremental feature and
release work with meaningful messages; no history rewrite was performed.

## Major Problems Found

No confirmed P0 exposed secret or immediately destructive flaw was established.

| Priority | Finding and evidence | Result |
| --- | --- | --- |
| P1 | Recovery root assumed dict; invalid path entries reach Qt restoration (`core/files/recovery.py`) | Validate version/root/list/text/path, ignore invalid entries and retain valid ones |
| P1 | Diagnostic stderr grows without bound (`MainWindow.program_error_output`) | Retain latest 250,000 characters |
| P1 | Delayed Stop may kill a subsequent run (`ProcessRunner.stop`) | Generation and stopping-state guard |
| P1 | Invalid executable test blocks inside `QProcess.start()` | Reproduced/localized, unresolved; full suite unverified |
| P1 | Wheel fails with current Hatchling due to duplicate force inclusion (`pyproject.toml`) | Reproduced, fixed, wheel built and resources loaded |
| P1 | Dispatch tag interpolation into PowerShell permits input to become source text | Environment-based tag/SHA, validation, signed/unsigned checkout target |
| P2 | Each output read decodes UTF-8 independently, corrupting split characters | Stateful per-channel decoders and final flush |
| P2 | Imported-file or edited-source traceback navigates to unrelated text | File/source/line checks, malformed-path handling |
| P2 | Frozen missing bundle can use GUI executable as Python | Fail closed with unavailable runtime |
| P2 | Untouched nonempty starter buffers are clean and excluded from recovery/prompts | Dirty untitled starter state |
| P2 | Canceling window close already terminates current program | Stop only after all document prompts accept close |
| P2 | Recovery deletion error can abort accepted close | Log deletion failure and allow close |
| P2 | Incomplete signing-certificate ignores | Ignore PFX/P12 |
| P2 | Editable-install-only CI misses wheel build; dependency consistency unchecked | Wheel build in quality matrix; pip check in all workflows |

Release input severity is conditioned on who can dispatch the workflow; it is not a
public unauthenticated endpoint. Existing tags can override `--target` semantics and
must still be verified before draft publication. No release was created here.

## Changes Implemented

- `core/files/recovery.py`: conservative schema validation without a data migration.
- `core/runtime/manager.py`: frozen builds require the bundle; source fallback preserved.
- `services/process_runner.py`: incremental decoders and generation-aware forced Stop.
- `ui/main_window.py`: bounded diagnostics, conservative navigation, cancellation and
  recovery cleanup handling. Its existing coordination role remains intact.
- `ui/editor/document_editor.py`: untitled nonempty content starts modified.
- `pyproject.toml`: remove duplicate forced resource inclusion, retaining JSON in wheels.
- `.github/workflows/`: safer tag data, checkout target, dependency consistency and wheel gate.
- `.gitignore`: signing certificates and diagnostic pytest temp directories.
- New Qt fixture/MainWindow/packaging/release tests; expanded recovery, runtime,
  process-stream and atomic-save failure regressions.
- README, continuity, architecture, decisions, roadmap, and testing guide updated.

## Architecture

```text
app / QApplication
    -> MainWindow + editor / console / dialogs
        -> pure files, execution request/output, runtime, error services
        -> pure learning libraries/progress -> bundled JSON
        -> QSettings / local recovery
        -> ProcessRunner (Qt adapter) -> separate learner Python
build tools -> pinned runtime + frozen GUI + notices -> per-user installer
```

Core and learning models stay independent of Qt. Widgets handle UI interactions;
MainWindow coordinates lifecycle. Runtime validation and file persistence are concrete
services, not generic repository layers. The runtime Protocol has two real implementations
and is defensible. No new application dependency or architectural layer was introduced.
New decisions 009/010 document context, alternatives, trade-offs, and consequences.

## Critical Workflows

| Workflow | Protection and limits |
| --- | --- |
| Open UTF-8/BOM Python source | DocumentService tests for extension, encoding, Unicode; opening does not execute |
| Save and Save As | Atomic sibling/fsync/replace; original file retained when replace fails |
| Close dirty tab/window | Save/discard/cancel prompts; component cancellation regression; live-child shutdown unverified |
| Recover edited/starter buffers | Version-1 atomic JSON, malformed-entry tests, untouched-starter snapshot regression |
| Prepare execution | Typed request paths/arguments, runtime validation, frozen bundle guard, cancel-save regression |
| Stream output/input | Real QProcess Unicode/stdin tests, incremental decoding, bounded visible/diagnostic output |
| Stop / duplicate prevention | Existing real child tests plus stale-generation callback regression; descendants unmanaged |
| Complete after tab switch/import/edit | Original run path/source retained; component navigation tests |
| Learn and persist completion | Stable IDs/order/compilable snippets and pure progress tests; manual grading only |
| Build distributable package | Actual wheel/isolated curriculum loads, traversal/checksum/missing-artifact tests |
| Installer/release | Static notice/installer contracts and tag-data tests; signing and clean-machine QA outstanding |

## Testing Strategy

Pure unit tests protect domain/file/runtime invariants. Offscreen QApplication component
checks isolate settings/recovery under temporary paths. Process integration tests execute
real child scripts; they are not solely tests of mocks. Packaging negative tests inspect
actual temporary ZIPs and cached bad archives. CI retains the full suite, lint and format
checks; no failing case was removed or suppressed.

New selected regressions were run against original source (temporarily restored from HEAD,
then restored in a finally block): **10 failed, 6 passed, 14 deselected**. They reproduced
malformed recovery roots/entries, frozen fallback, unbounded stderr, imported/edited source
navigation and fragmented UTF-8. This run excluded the blocking launch-failure case.
The wheel duplication was reproduced with Hatchling 1.32.4 before removing force inclusion.

Local checks on Python 3.13.15:

- Selected pytest suite: **70 passed, 1 deselected**; invalid-executable excluded explicitly.
- Full suite attempted: blocked at invalid executable, interrupted. Faulthandler showed
  `ProcessRunner.run` at `QProcess.start()`. An event-loop timer cannot bound that call.
- Ruff lint and format checks passed; `git diff --check` passed.
- `pip check` passed. This checks compatibility, not vulnerabilities.
- Initial wheel attempt lacked Hatchling; installed the already-declared build backend locally.
  Next build reproduced duplicate resource failure; fixed build succeeded.
- `pip wheel . --no-build-isolation --no-deps --wheel-dir build/audit-wheel` succeeded.
  Archive paths were unique; isolated Python loaded 18 lessons and four examples from the wheel.
- Windows frozen portable/installer, signing, Python 3.11 matrix and CI runs were not executed.
  No release artifacts were available/validated for clean-machine testing in this session.

Dark/light workspace renders were attempted with the offscreen Qt platform. Layout and
colors rendered, but text appeared as missing-glyph squares; this environment could not
validate font readability. These images are ignored build diagnostics, not theme QA evidence.

No full end-to-end suite, screen-reader QA, exhaustive lesson execution, vulnerability scanner,
transitive lockfile verification or benchmark was performed. The stale Stop regression
simulates callback delivery rather than waiting through a real two-second restart cycle.

## Security Review

No current tracked credential-like filename was identified in inventory. This does not
prove secret-free history; no secret contents were printed. Preserve signing environment
credentials, always-run temporary certificate removal, unsigned preview disclosures and
canonical license texts. Recovery/source and console input remain private local data.

Shell-free execution remains intact. Learner code inherits environment and user permissions;
it can access files, network and credentials. It is explicitly not sandboxed. Adding an
unproven sandbox or stripping arbitrary environment values would change the product contract.

Upstream advisory review used [Qt's security advisory list](https://wiki.qt.io/List_of_known_vulnerabilities_in_Qt_products).
It lists issues affecting VNC Server and Qt XML in versions including 6.11.2. PyNivo does
not implement VNC or XML serialization; no reachable exploit path for those entries was
established by source inspection. This is an inference, not a vulnerability-free certification.
Do not blindly upgrade Qt: verify reachability, compatibility and LGPL source notices together.

## Data Integrity

Source saves preserve UTF-8 and atomic replacement; failure regression proves original
content survives a locked replacement. Recovery remains a compatible version-1 separate
snapshot, never writes directly over source, and retains good entries among malformed ones.
QSettings stores preferences/completion with stable curriculum identifiers. No database
transactions or migrations apply. Crash recovery still has a 15-second loss window, plaintext
storage and no full saved-tab session. Atomic replacement does not imply every filesystem's
power-loss durability or concurrent-instance coordination.

## Generated-code / Maintainability Signals

Concrete signals were duplicate wheel resource inclusion and documentation promising complete
traceback visibility despite output trimming. Both were corrected. MainWindow is sizeable and
combines several UI workflows; it merits future extraction only when a concrete change needs
it. Regex highlighting/bracket/error helpers trade fidelity for simplicity, with known limits.
Some UI methods lack annotations and static contract tests cannot establish live behavior.
No evidence justified deleting runtime interfaces, dataclasses or useful documentation merely
because they resemble generated code. No TODO/factory explosion or fake database layer was found.

## Remaining Technical Debt

- Resolve launch stall with a bounded external reproduction on an unrestricted Windows machine;
  compare Qt versions and capture native diagnostics before selecting a fix.
- Explicitly manage live-child shutdown/destruction and decide descendant cleanup requirements.
- High-volume console trimming redraws retained output; bracket matching scans source on cursor
  movement and mixes Qt UTF-16 positions with Python character indexes for supplementary Unicode.
- Hardcoded bracket colors, limited focus/accessibility labels and no screen-reader/contrast QA.
- Recovery/settings lack concurrent-instance coordination; invalid settings and disk-full startup
  logging/recovery-clear restoration paths need further failure handling.
- Lesson-dialog edits are not persisted; marking complete can refresh starter text. Full saved-tab
  persistence and automated grading remain optional product decisions.
- Dev/build dependency ranges and action tags are not a locked supply chain. No automatic dependency
  security gate or full typed analysis exists. Coordinate repeated version metadata before bumps.
- Build download has no explicit timeout; reused `--skip-portable` artifacts are not revalidated.
- Wheel curriculum is verified, but installed-wheel branding/compliance UI and complete installer
  resources still require installed-environment checks.

## Remaining Risks

The synchronous invalid-executable stall may affect unusual runtime failures; ordinary runs
validate Python first but that validation also uses a subprocess. GUI runtime validation can
block for up to five seconds. Delayed process-tree cleanup and shutdown are not fully verified.
Disk failures/concurrent instances can lose or overwrite local recovery. A traceback tail can
omit useful earlier context. User-run code has ordinary privileges. No trusted-signing, live
release, clean-machine installer or accessibility readiness is established.

## Final Score

**7.2/10**, up from **6.5/10**; per-category final scores are alongside the baseline above.
This is stronger portfolio quality, with useful regression evidence, still below proven
production quality. Scores do not claim verification beyond the checks explicitly recorded.

## Recommended Next Steps

1. Resolve the native launch stall and demonstrate a full-suite pass on both supported CI Pythons.
2. Verify live-child close/Stop/restart and decide whether Windows process-tree ownership is required.
3. Record clean Windows 10/11 installer, keyboard/screen-reader and both-theme results with checksums.
4. Validate existing-tag commit identity, signing credentials and artifact notices before release.
5. Lock a tested build toolchain, add reachable-advisory review and cover reused artifact/download failures.

## Intentionally Unchanged

Kept Qt, the offline architecture, process adapter and MainWindow coordination; their boundaries
are appropriate for this scale. Kept stable lesson IDs/version-1 recovery and manual completion.
Did not add accounts, telemetry, database, packages, cloud APIs, generic repositories, interfaces
for appearances or a new grading engine. Did not rewrite history, bump versions, alter license
texts, configure credentials, publish releases, or fabricate maintainer security contacts.
These would add scope or require external verification rather than fix established defects.
