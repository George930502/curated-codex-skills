# Compatibility evidence

This matrix separates automated evidence from manual exercise. It does not
promise that every Codex account or client exposes experimental native tools.

| Environment | Installer | Evidence for `v0.1.0` | Limit |
|---|---|---|---|
| Ubuntu Linux | `install.sh` | [CI run 29283361400](https://github.com/George930502/curated-codex-skills/actions/runs/29283361400): validation, tests, isolated install, feature diagnostics, and source parity at release implementation commit `76f46f7` | GitHub-hosted runner |
| macOS | `install.sh` | Same matrix run and checks at `76f46f7` | GitHub-hosted runner |
| Windows PowerShell | `install.ps1` | Same matrix run and checks at `76f46f7` | GitHub-hosted runner; native UI availability remains client-dependent |
| WSL | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |
| Git Bash | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |

[CodeQL run 29283361392](https://github.com/George930502/curated-codex-skills/actions/runs/29283361392)
analyzed the Python code at the same release implementation commit. Subsequent
documentation-only evidence updates do not broaden these compatibility claims.
