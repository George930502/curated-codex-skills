# Curated Codex Skills

A curated, production-tested collection of reusable Codex skills and workflows.
Each skill is selected for a concrete workflow, kept auditable to its sources,
and exercised through the platforms on which its behavior differs.

> **Preview:** `v0.1.0` established the maintenance contract. The compatible
> `v0.1.1` update hardens upgrades and compatibility checks. Interfaces may
> evolve before `v1.0.0`; changes are tracked in the
> [changelog](CHANGELOG.md).

## Catalog

| Skill | Purpose | Origin |
|---|---|---|
| `prompt-review-and-dispatch` | Clarify, polish, approve, and dispatch a prompt into a verified Codex task. | Original composition |
| `prompt-master-gpt5` | Audit or produce a lean GPT-5.6 prompt. | Distilled from `nidhinjs/prompt-master` plus OpenAI guidance |
| `grill-with-docs` | Stress-test plans while maintaining domain language and decisions. | Adapted from `mattpocock/skills` |
| `grilling` | Resolve decisions one native Codex question at a time. | Adapted from `mattpocock/skills` |
| `domain-modeling` | Maintain project language and durable decisions. | Adapted from `mattpocock/skills` |

[`SOURCES.md`](SOURCES.md) pins every upstream commit, source path, hash, and
adaptation. [`AUTHORING-AUDIT.md`](AUTHORING-AUDIT.md) records the authoring
standards used. MIT notices are preserved in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Compatibility

The installers target Codex's documented user skill directory,
`$HOME/.agents/skills` (`%USERPROFILE%\.agents\skills` on Windows).

The repository exercises installation and validation on GitHub-hosted Linux,
macOS, and Windows runners, plus Python 3.10 through 3.14. Windows CI executes
the shell installer through Git Bash and the PowerShell installer through both
Windows PowerShell 5.1 and PowerShell 7. WSL has no retained runner artifact and
is not an independently auditable compatibility claim. Native approval
additionally depends on the Codex host exposing `request_user_input`;
Windows setup is documented in
[`docs/windows-native-input.md`](docs/windows-native-input.md).
The evidence and limits for each surface are recorded in the
[`compatibility matrix`](docs/compatibility.md).

The skills require an interactive, authenticated Codex surface. They do not
bundle credentials, enable experimental features silently, or claim support
for non-Codex agents.

## Install

### macOS, Linux, WSL, or Git Bash

```bash
git clone https://github.com/George930502/curated-codex-skills.git
cd curated-codex-skills
bash scripts/install.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/George930502/curated-codex-skills.git
Set-Location .\curated-codex-skills
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

The installers copy all catalog skills and report whether
`default_mode_request_user_input` is available and enabled. They do not change
Codex configuration. Reinstalling replaces catalog-owned skill directories so
deleted files do not linger; unrelated skill directories are preserved. Codex
detects skill changes automatically, but a restart may be needed if they do not
appear. To test an install without touching your real home, use:

```bash
SKILLS_INSTALL_DIR="$(mktemp -d)/skills" bash scripts/install.sh
```

```powershell
$target = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid())
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Destination $target
```

## Validate

Validation is self-contained and uses only the Python standard library:

```bash
python3 scripts/validate.py --skills-dir skills
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
```

On Windows, replace `python3` with `py -3`. These are the same repository checks
run by CI. Python 3.10 is the minimum supported version. Installer tests always
use temporary destinations; see
[`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contribution gate.

## Project contract

- [Contributing](CONTRIBUTING.md) — change flow, skill admission, and checks
- [Security](SECURITY.md) — private vulnerability reporting and scope
- [Support](SUPPORT.md) — questions, defects, and native-input diagnostics
- [Governance](GOVERNANCE.md) — maintainership and decision policy
- [Roadmap](ROADMAP.md) — addition criteria and near-term direction
- [Releases](docs/releasing.md) — versioning and release procedure
- [Code of Conduct](CODE_OF_CONDUCT.md)

This project is licensed under the [MIT License](LICENSE).
