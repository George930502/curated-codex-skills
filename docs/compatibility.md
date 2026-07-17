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

## Published v0.1.1

| Dimension | Executed coverage | Evidence boundary |
|---|---|---|
| Operating systems | `ubuntu-latest`, `macos-latest`, `windows-latest` | GitHub-hosted images, not arbitrary hardware or local policy |
| Shell installers | Bash on Ubuntu and macOS; Git Bash on Windows | Actual shell processes with isolated temporary destinations |
| PowerShell installers | Windows PowerShell 5.1 and PowerShell 7 on Windows | Actual script execution, not parser-only inspection |
| Python | CPython 3.10, 3.11, 3.12, 3.13, and 3.14 on Ubuntu | Standard-library validator and tests; macOS and Windows use 3.11; no PyPy claim |
| Paths and upgrades | Spaces, Unicode, file collisions, repeat install, failed-copy retention, failed-swap rollback, non-fatal Bash/Git Bash post-commit cleanup failure, exact UTF-8 and legacy PowerShell marked-transaction cleanup across shells, interrupted-backup recovery, catalog-wide recovery preflight before mutation, strict transaction structure, ambiguous-backup refusal, transaction and marker-alias rejection, stale-file removal, unrelated-skill preservation, structural source parity with catalog, skill-root, and descendant aliases rejected, local/drive/UNC/double-slash root guards, and source/destination aliases | POSIX rejects implementation-defined double-slash paths, folds three or more leading slashes, and canonicalizes other aliases; Windows rejects reparse and substituted-drive aliases; deterministic temporary directories only |
| Codex capability | CLI absent; feature absent, enabled, disabled, malformed, command failure, and LF/CRLF output | Fixtures prove installer branching, not historical Codex binaries or UI |
| Skill discovery | Exact source parity is executed in isolated destinations; the documented `$HOME/.agents/skills` default is asserted statically | CI does not authenticate or launch an interactive Codex client |

Executable commit `d595965` passed [CI run
29329905338](https://github.com/George930502/curated-codex-skills/actions/runs/29329905338)
and [CodeQL run
29329905337](https://github.com/George930502/curated-codex-skills/actions/runs/29329905337).
The CI run contains successful Ubuntu, macOS, Windows, all five Ubuntu Python-version,
and aggregate jobs. Its Windows Server 2025 job directly identified and ran
Windows PowerShell 5.1, PowerShell 7, and Git Bash before exercising each
installer. The release notes link the later protected-main runs because their
identifiers cannot exist in this candidate commit without a self-referential
evidence update.

Protected main subsequently passed [CI run
29331389046](https://github.com/George930502/curated-codex-skills/actions/runs/29331389046)
and [CodeQL run
29331389139](https://github.com/George930502/curated-codex-skills/actions/runs/29331389139)
at the immutable `v0.1.1` commit `5e3d3cf`.

## v0.1.2 evidence boundary

The `v0.1.2` change affects only agent-authored native-control language and its
repository checks. It does not change installer behavior or broaden the
platform matrix above. Release still requires the complete Linux, macOS,
Windows, and Python matrix because installed source parity and all five skill
contracts are validated on every candidate.

## Direct native-input observation

Manual scenario: invoke `$prompt-review-and-dispatch` with an incomplete prompt
in a Default-mode desktop task; select the native alignment choice; inspect the
displayed exact draft; leave or return an empty approval answer and confirm no
execution; resume the task; then select the native approval option and confirm
the exact approved prompt continues visibly in the same task, with no new
thread and no `send_message_to_thread` call. Repeat with an explicitly chosen
`background-task` and confirm the verified destination and one thread-send
result.

On 2026-07-14, the active Codex desktop task on Linux reported
`codex-cli 0.144.1` with `default_mode_request_user_input` enabled. The task
displayed the English `Aligned (Recommended)` and `Approve (Recommended)`
controls, accepted explicit clickable selections, preserved state after empty
answers, and dispatched only after approval was selected on the pre-repair
background path. This is a reproducible manual report for that observed client
and configuration, but it has no retained independent GUI artifact and is not
an independently auditable or universal client/version claim.
The current contract makes every agent-authored native-control string English
by default while normal assistant prose remains language-adaptive. The client
controls the displayed label and localization of its built-in `Other` choice.
The checked-in contract requires the same unanswered control to be reissued
without a retry limit while the task remains active. Repository checks enforce
that requirement statically; they do not prove how every client renders or
retains its native UI.
The clarification/grilling control was not separately recorded in this manual
observation; its coverage is limited to the static contract and executable
capability fixtures above.

## Current-conversation execution contract

The working-tree repair for `prompt-review-and-dispatch` defaults to
`current-conversation` execution. After the native approval selection, the
agent continues the exact approved prompt in the same running task; it does not
call the background-only `send_message_to_thread` tool. A separate
`background-task` mode remains opt-in and retains the verified destination and
explicit approval gates. Inline completion requires the exact draft to remain
unchanged as verified by matching SHA-256 hashes for the approved and executed
UTF-8 bytes, observable same-task continuation, and actual result, artifact, or
test evidence that the approved prompt's success criteria are satisfied;
continuation start alone is not completion. This behavior is a skill contract
and does not claim that the Codex client exposes a foreground message-injection
API.

WSL and historical Codex binaries remain unverified surfaces for `v0.1.2`.
They use the capability policy: install may succeed, but workflows block if the
active client does not expose native input or task dispatch.
