# Compatibility evidence

This matrix separates automated evidence from manual exercise. It does not
promise that every Codex account or client exposes experimental native tools.

| Environment | Installer | Evidence for `v0.1.0` | Limit |
|---|---|---|---|
| Ubuntu Linux | `install.sh` | [CI run 29284432670](https://github.com/George930502/curated-codex-skills/actions/runs/29284432670): validation, tests, isolated install, feature diagnostics, and source parity at final executable/test commit `d4ce21f` | GitHub-hosted runner |
| macOS | `install.sh` | Same matrix run and checks at `d4ce21f` | GitHub-hosted runner |
| Windows PowerShell | `install.ps1` | Same matrix run and checks at `d4ce21f` | GitHub-hosted runner; native UI availability remains client-dependent |
| WSL | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |
| Git Bash | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |

[CodeQL run 29284432454](https://github.com/George930502/curated-codex-skills/actions/runs/29284432454)
analyzed the Python code at the same commit. The later commit that records these
immutable run links changes this evidence document only.
