# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions use [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-14

### Fixed

- Make upgrades replace each catalog-owned skill so removed files cannot remain
  installed, while preserving unrelated user skills and rolling back a failed
  replacement.
- Distinguish missing, disabled, malformed, and failed Codex native-input
  capability diagnostics.
- Refuse destructive install destinations at the filesystem root or inside the
  packaged source catalog; canonicalize POSIX aliases and reject Windows
  reparse or substituted-drive aliases without creating rejected paths.

### Changed

- Exercise installers with spaces, Unicode, collisions, repeat installs, source
  parity, Windows PowerShell 5.1, PowerShell 7, Git Bash, and failure fixtures.
- Validate Python 3.10 through 3.14 on Ubuntu in addition to the Python 3.11
  Linux, macOS, and Windows installer matrix.
- Enforce the shared persistent native-input contract as a repository invariant.

## [0.1.0] - 2026-07-14

### Added

- Initial catalog: `prompt-review-and-dispatch`, `prompt-master-gpt5`,
  `grill-with-docs`, `grilling`, and `domain-modeling`.
- Cross-platform installers with isolated-destination support.
- Self-contained validation, repository checks, and Linux/macOS/Windows CI.
- Contribution, security, support, governance, provenance, and release contracts.

[Unreleased]: https://github.com/George930502/curated-codex-skills/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/George930502/curated-codex-skills/releases/tag/v0.1.1
[0.1.0]: https://github.com/George930502/curated-codex-skills/releases/tag/v0.1.0
