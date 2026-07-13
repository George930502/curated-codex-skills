# Compatibility evidence

This matrix separates automated evidence from manual exercise. It does not
promise that every Codex account or client exposes experimental native tools.

| Environment | Installer | Evidence for `v0.1.0` | Limit |
|---|---|---|---|
| Ubuntu Linux | `install.sh` | [CI run 29282436986](https://github.com/George930502/curated-codex-skills/actions/runs/29282436986): validation, tests, isolated install, feature diagnostics, and source parity at `dc85aad` | GitHub-hosted runner |
| macOS | `install.sh` | Same matrix run and checks at `dc85aad` | GitHub-hosted runner |
| Windows PowerShell | `install.ps1` | Same matrix run and checks at `dc85aad` | GitHub-hosted runner; native UI availability remains client-dependent |
| WSL | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |
| Git Bash | `install.sh` | Prior manual exercise was reported in the release brief | No retained artifact; not an independently auditable `v0.1.0` compatibility claim |

[CodeQL run 29282437076](https://github.com/George930502/curated-codex-skills/actions/runs/29282437076)
analyzed the release-candidate Python code at the same commit. The final release
check must replace or supplement this candidate evidence if review fixes change
the commit.
