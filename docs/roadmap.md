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

- [ ] Bound diagnostic stderr while preserving useful traceback context.
- [ ] Validate recovery JSON root/entry types and malformed valid JSON safely.
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
- [ ] Guard frozen-app fallback when the private learner runtime is absent.
- [ ] Review smoke-mode timer/settings side effects and untouched starter-tab recovery.

## Testing improvements

- [ ] Investigate the local stall in `test_runner_reports_unlaunchable_executable`;
  the 2026-10-01 full run was interrupted, while the other 41 cases passed.

- [ ] Add malformed-valid-JSON recovery and high-volume stderr regressions.
- [ ] Add MainWindow save/cancel/run, tab-switch, imported-error, and stop/restart tests.
- [ ] Cover dialog find/replace, onboarding/settings, lesson/progress, recovery workflows.
- [ ] Test checksum failure, ZIP traversal, distribution completeness, and smoke failures.
- [ ] Preserve a clean-machine installed-app QA record distinct from GUI smoke checks.

## Security improvements

- [ ] Add PFX/P12 and appropriate credential-file ignore patterns; none found tracked
  in this review, but current patterns are incomplete.
- [ ] Pass dispatch inputs through environment variables instead of interpolating
  PowerShell source; verify signed-release tag/SHA targeting.
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
