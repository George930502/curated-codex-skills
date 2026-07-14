# Production v0.1.1 specification

`v0.1.1` is a compatible hardening release reviewed from immutable tag
`v0.1.0`. It must preserve all five skill identities, provenance, licenses, and
the prompt audit, native clarification, alignment, exact approval, and verified
dispatch workflow.

Acceptance requires:

- a deletion-first audit with no speculative framework or dependency;
- exact catalog upgrades that remove stale files and preserve unrelated skills;
- isolated install and capability-diagnostic tests on Linux, macOS, Windows
  PowerShell 5.1, PowerShell 7, and Git Bash;
- CPython 3.10 through 3.14 validation;
- separate static-contract, executable-fixture, and directly observed native UI
  evidence, without presenting fixtures as GUI proof;
- current primary-source testing decisions and explicit unsupported surfaces;
- green protected CI and CodeQL plus fresh Standards and Spec reviews with no
  findings; run a fresh read-only Claude review when available, but record and
  ignore a Claude session-limit failure rather than blocking the release;
- an annotated public `v0.1.1` prerelease synchronized with `origin/main`.

The release must not move `v0.1.0`, mutate a real user home or global Codex
configuration, require live credentials in CI, weaken approval or dispatch,
discard notices, or claim universal hardware, client, or version compatibility.

Review sequencing is intentionally two-phase: fresh reviewers assess the
candidate diff and release readiness before publication, so the not-yet-created
protected-main run, tag, and release are gates rather than candidate defects.
After clean reviews, merge and protected-main CI must pass before the tag is
created; final verification then proves the publication requirements above.
