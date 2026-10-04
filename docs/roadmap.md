# Roadmap

Snapshot: 2026-10-01, baseline `8f5a3a4`. Checked items indicate implemented code
or documentation, not certified production readiness. Unchecked items are
recommendations unless explicitly identified as existing project expectations.

## Completed

- [x] Multi-tab editor, file lifecycle, UTF-8 atomic saves, recent files.
- [x] Child execution with output/input, Stop, duplicate prevention, original-source tracking.
- [x] Welcome, examples, 18 lessons, hints, manually persisted completion.
- [x] Deterministic traceback guidance and spelling suggestions.
- [x] Themes, editor text tools, persisted preferences.
- [x] Periodic modified-buffer recovery and bounded visible output.
- [x] Private runtime discovery, verified Windows portable build, per-user installer.
- [x] Windows CI, preview artifacts, separate unsigned/signed draft release paths.
- [x] Apache attribution, LGPL materials, cross-platform license hash checks.
- [x] Agent instructions, continuity, architecture, decisions, and handoff documents.

## Current / in progress

Current stage is the 0.1.0 Windows prerelease preview; latest work focuses on
licensing/distribution. No tracked assigned task, feature branch, or TODO/FIXME
proves a specific implementation is actively underway.

- [ ] Trusted signing is planned per README/preview docs; verify certificate
  readiness and actual release availability separately.

## Next

- [x] Bound diagnostic stderr while preserving useful traceback context.
- [x] Validate recovery JSON root/entry types and malformed valid JSON safely.
- [ ] Test rapid stop/restart generation handling; review descendant cleanup and
  traceback filename validation before editor navigation.
- [ ] Record clean Windows 10/11 install/uninstall, runtime, welcome, I/O, Stop,
  recovery, and both-theme QA results.

## Later

- [ ] Design isolated package support if product scope requires it; ordinary pip
  against the embeddable runtime is not the established strategy.
- [ ] Consider other platform distributions only after requirements are established.
- [ ] Consider full session/draft persistence and automated lesson grading if needed;
  these are optional future scope, not confirmed requirements.

## Technical debt

- [ ] Centralize or validate repeated app version metadata before version bumps.
- [ ] Use shared bracket colors; assess syntax-aware matching and large-file costs.
- [x] Guard frozen-app fallback when the private learner runtime is absent.
- [ ] Review smoke-mode timer/settings side effects and untouched starter-tab recovery.

## Testing improvements

- [ ] Investigate the local stall in `test_runner_reports_unlaunchable_executable`;
  the 2026-10-01 full run was interrupted, while the other 41 cases passed.

- [x] Add malformed-valid-JSON recovery and high-volume stderr regressions.
- [ ] Add MainWindow save/cancel/run, tab-switch, imported-error, and stop/restart tests.
- [ ] Cover dialog find/replace, onboarding/settings, lesson/progress, recovery workflows.
- [ ] Test checksum failure, ZIP traversal, distribution completeness, and smoke failures.
- [ ] Preserve a clean-machine installed-app QA record distinct from GUI smoke checks.

## Security improvements

- [x] Ignore PFX/P12 signing certificates; no tracked certificate found.
- [x] Pass dispatch tags/SHA through environment variables; both releases target checkout SHA.
- [ ] Verify any existing release tag resolves to the intended artifact commit.
- [ ] Establish a private reporting channel (existing SECURITY.md expectation).
- [ ] Configure trusted signing when available; preserve unsigned preview disclosures.
- [ ] Preserve warnings about user privileges/inherited environments and private
  data in plaintext recovery/console input.

## Documentation improvements

- [ ] Record actual release links, tested artifact checksums, signing status, and
  clean-machine QA only after verification.
- [ ] Keep handoff/test results current after significant sessions.
- [ ] Record future accepted decisions with evidence/rationale; keep recommendations
  distinct from confirmed product requirements.

## Audit progress — 2026-10-05

- [x] Incremental UTF-8 output decoding and execution-generation Stop guard.
- [x] Matching-file/unchanged-source traceback navigation and component tests.
- [x] Untouched starter-buffer dirty state/recovery and atomic-save failure regression.
- [x] Checksum/traversal/distribution-completeness packaging regressions.
- [x] Reproduce and fix duplicate wheel resources; build wheels in CI.
- [x] Dependency consistency gate and dated engineering scorecards.
- [ ] Resolve invalid-executable stall inside QProcess.start; full local suite remains blocked.
- [ ] Exercise real rapid Stop/restart over the complete timer interval, descendant cleanup,
  and GUI shutdown with a live child; existing regression simulates a stale callback.
- [ ] Lock tested release tooling/transitive dependencies and review reachable upstream advisories.
- [ ] Revalidate reused portable artifacts before installer compilation.

See [ENGINEERING_AUDIT.md](../ENGINEERING_AUDIT.md) and [testing](testing.md).
