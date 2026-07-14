# Compatibility evidence

This matrix separates executable CI, deterministic capability fixtures, and
manual client observation. It does not promise that every Codex account,
version, or surface exposes experimental native tools.

## Published v0.1.0

| Environment | Installer | Evidence for `v0.1.0` | Limit |
|---|---|---|---|
| Ubuntu Linux | `install.sh` | [CI run 29285534958](https://github.com/George930502/curated-codex-skills/actions/runs/29285534958): validation, tests, isolated install, feature diagnostics, and source parity at final code/workflow commit `3dd1bcb` | GitHub-hosted runner |
| macOS | `install.sh` | Same matrix run and checks at `3dd1bcb` | GitHub-hosted runner |
| Windows PowerShell | `install.ps1` | Same matrix run and checks at `3dd1bcb` | GitHub-hosted runner; native UI availability remains client-dependent |
| WSL | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |
| Git Bash | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |

[CodeQL run 29285534891](https://github.com/George930502/curated-codex-skills/actions/runs/29285534891)
analyzed the Python code at the same commit. The later commit that records these
immutable run links changes this evidence document only. The `v0.1.0` tag
remains immutable.

## v0.1.1 candidate matrix

| Dimension | Executed coverage | Evidence boundary |
|---|---|---|
| Operating systems | `ubuntu-latest`, `macos-latest`, `windows-latest` | GitHub-hosted images, not arbitrary hardware or local policy |
| Shell installers | Bash on Ubuntu and macOS; Git Bash on Windows | Actual shell processes with isolated temporary destinations |
| PowerShell installers | Windows PowerShell 5.1 and PowerShell 7 on Windows | Actual script execution, not parser-only inspection |
| Python | CPython 3.10, 3.11, 3.12, 3.13, and 3.14 on Ubuntu | Standard-library validator and tests; macOS and Windows use 3.11; no PyPy claim |
| Paths and upgrades | Spaces, Unicode, file collisions, repeat install, failed-copy retention, failed-swap rollback, stale-file removal, unrelated-skill preservation, source parity, local/drive/UNC root guards, and source/destination aliases | POSIX canonicalizes aliases; Windows rejects reparse and substituted-drive aliases; deterministic temporary directories only |
| Codex capability | CLI absent; feature absent, enabled, disabled, malformed, and command failure | Fixtures prove installer branching, not historical Codex binaries or UI |
| Skill discovery | Exact source parity is executed in isolated destinations; the documented `$HOME/.agents/skills` default is asserted statically | CI does not authenticate or launch an interactive Codex client |

Executable commit `02511e9` passed [CI run
29314074529](https://github.com/George930502/curated-codex-skills/actions/runs/29314074529)
and [CodeQL run
29314074516](https://github.com/George930502/curated-codex-skills/actions/runs/29314074516).
The CI run contains successful Ubuntu, macOS, Windows, all five Ubuntu Python-version,
and aggregate jobs. Its Windows Server 2025 job directly identified and ran
Windows PowerShell 5.1, PowerShell 7, and Git Bash before exercising each
installer. Final protected-main links replace this candidate evidence before
release.

## Direct native-input observation

Manual scenario: invoke `$prompt-review-and-dispatch` with an incomplete prompt
in a Default-mode desktop task; select the native alignment choice; inspect the
displayed exact draft; leave or return an empty approval answer and confirm no
dispatch; resume the task; then select native `同意` and confirm one thread-send
result.

On 2026-07-14, the active Codex desktop task on Linux reported
`codex-cli 0.144.1` with `default_mode_request_user_input` enabled. The task
displayed persistent native alignment and approval controls, accepted explicit
clickable selections, preserved state after empty answers, and dispatched only
after `同意` was selected. This is a reproducible manual report for that observed
client and configuration, but it has no retained independent GUI artifact and
is not an independently auditable or universal client/version claim.
The clarification/grilling control was not separately recorded in this manual
observation; its coverage is limited to the static contract and executable
capability fixtures above.

WSL and historical Codex binaries remain unverified surfaces for `v0.1.1`.
They use the capability policy: install may succeed, but workflows block if the
active client does not expose native input or task dispatch.
