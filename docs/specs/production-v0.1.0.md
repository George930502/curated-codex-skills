# Production v0.1.0 specification

The `v0.1.0` preview establishes Curated Codex Skills as a public umbrella
collection while preserving the five existing skill identities and provenance.

Starting evidence supplied for this release records successful installation on
Windows, macOS, Linux, WSL, and Git Bash. Automated release-candidate evidence
must independently exercise Linux, macOS, and Windows; WSL and Git Bash remain
an unretained manual report and must not be presented as CI coverage or an
independently auditable compatibility guarantee.

Acceptance requires:

- consistent `curated-codex-skills` repository identity and public metadata;
- documented scope, compatibility, install, validation, contribution, support,
  security, governance, provenance, roadmap, versioning, and release policy;
- self-contained skill and repository validation;
- isolated installer smoke tests on Linux, macOS, and Windows;
- least-privilege, deterministic CI and dependency maintenance;
- clean fresh-context Standards and Spec reviews from pre-change commit
  `9ca9a37c3c5f6bdf77af2e6ec56cbf8565e2f9d7`;
- a public `main`, annotated `v0.1.0` tag, and GitHub prerelease whose commit is
  synchronized with the local checkout.

The release must not claim support beyond the exercised environments, require
live Codex credentials for CI, mutate a real user home, weaken approval or
dispatch gates, or discard third-party license notices.
