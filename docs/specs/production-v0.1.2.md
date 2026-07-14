# Production v0.1.2 specification

`v0.1.2` is a compatible native-control language release reviewed from the
immutable `v0.1.1` tag, peeled commit
`5e3d3cf4d3684c17a57e65e5ff8df636d4d230dd`.

Every agent-authored native header, question, option label, and option
description must default to English, regardless of the conversation language.
Alignment uses `Aligned (Recommended)` and `Needs revision`; approval uses
`Approve (Recommended)` and `Reject`. The recommended option remains first.
Only `Approve (Recommended)` authorizes dispatch. Rejection, a free-form
`Other` answer, blank output, malformed output, or missing input never does.
The host owns the built-in `Other` control and its localization.

The release must preserve language-adaptive assistant prose, one blocking
native question at a time, unlimited identical reissue after an empty answer,
verified destination identity, exact-prompt approval, and byte-for-byte
dispatch. It must preserve all five skill identities, installer behavior,
provenance, licenses, notices, and immutable `v0.1.0` and `v0.1.1` objects.

Acceptance requires:

- self-contained source validation, repository checks, and unit tests;
- mechanical rejection of missing canonical English labels and former fixed
  non-English native labels;
- isolated installer and installed-source parity checks on Linux, macOS,
  Windows PowerShell 5.1, PowerShell 7, and Git Bash;
- CPython 3.10 through 3.14 validation;
- separate static-contract, executable-fixture, and narrowly scoped current
  client evidence without presenting fixtures as GUI proof;
- green protected CI and CodeQL;
- fresh Standards and Spec reviews from `v0.1.1`, repeated until both return
  exactly `No findings.`;
- an annotated public `v0.1.2` prerelease synchronized with `origin/main`.

Review the candidate with `git diff v0.1.1...HEAD` and
`git log v0.1.1..HEAD --oneline`. A fresh read-only Claude review is optional
additional evidence; unavailability or a session limit is recorded but does
not replace or block the two required reviews.

The release must not mutate a real user home or global Codex configuration,
require live Codex credentials in CI, add a custom `Other` option, force normal
assistant prose to English, weaken approval or dispatch, or claim universal
client, historical-version, hardware, WSL, or GUI compatibility.

Reviewers assess the candidate before publication. Protected-main CI must pass
after merge before the annotated tag and prerelease are created; those future
objects are release gates, not candidate-diff defects.
