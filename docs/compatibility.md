# Compatibility evidence

This matrix separates executable CI, deterministic capability fixtures, and
manual client observation. It does not promise that every Codex account,
version, or surface exposes experimental native tools.

## Published v0.1.0

| Environment | Installer | Evidence | Limit |
|---|---|---|---|
| Ubuntu Linux | `install.sh` | [CI run 29285534958](https://github.com/George930502/curated-codex-skills/actions/runs/29285534958) at `3dd1bcb` | GitHub-hosted runner |
| macOS | `install.sh` | Same matrix run and commit | GitHub-hosted runner |
| Windows PowerShell | `install.ps1` | Same matrix run and commit | GitHub-hosted runner; native UI remained client-dependent |
| WSL | `install.sh` | Prior manual report only | No retained artifact; not an independently auditable claim |
| Git Bash | `install.sh` | Prior manual report only | No retained artifact in v0.1.0 |

[CodeQL run 29285534891](https://github.com/George930502/curated-codex-skills/actions/runs/29285534891)
analyzed the Python code at the same executable commit. The `v0.1.0` tag remains
immutable.

## v0.1.1 candidate matrix

| Dimension | Executed coverage | Evidence boundary |
|---|---|---|
| Operating systems | `ubuntu-latest`, `macos-latest`, `windows-latest` | GitHub-hosted images, not arbitrary hardware or local policy |
| Shell installers | Bash on Ubuntu and macOS; Git Bash on Windows | Actual shell processes with isolated temporary destinations |
| PowerShell installers | Windows PowerShell 5.1 and PowerShell 7 on Windows | Actual script execution, not parser-only inspection |
| Python | CPython 3.10, 3.11, 3.12, 3.13, and 3.14 | Standard-library validator and tests; no PyPy claim |
| Paths and upgrades | Spaces, Unicode, file collisions, repeat install, stale-file removal, unrelated-skill preservation, source parity | Deterministic temporary directories only |
| Codex capability | CLI absent; feature absent, enabled, disabled, malformed, and command failure | Fixtures prove installer branching, not historical Codex binaries or UI |
| Skill discovery | Installed tree equals packaged source under the documented user-skill layout | CI does not authenticate or launch an interactive Codex client |

The executable candidate passed [CI run
29309662837](https://github.com/George930502/curated-codex-skills/actions/runs/29309662837)
and [CodeQL run
29309662840](https://github.com/George930502/curated-codex-skills/actions/runs/29309662840).
The CI run contains successful Ubuntu, macOS, Windows, all five Python-version,
and aggregate jobs. Final protected-main links replace this candidate evidence
before release.

## Direct native-input observation

On 2026-07-14, the active Codex desktop task on Linux reported
`codex-cli 0.144.1` with `default_mode_request_user_input` enabled. The task
displayed persistent native alignment and approval controls, accepted explicit
clickable selections, preserved state after empty answers, and dispatched only
after `同意` was selected. This is direct task-level evidence for that observed
client and configuration; it is not automated GUI evidence and does not support
a universal client/version claim.

WSL and historical Codex binaries remain unverified surfaces for `v0.1.1`.
They use the capability policy: install may succeed, but workflows block if the
active client does not expose native input or task dispatch.
