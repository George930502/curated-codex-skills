# Testing strategy and tool decision

Reviewed 2026-07-14. The project is a small standard-library validator plus two
installers, not a Python package. The minimum useful stack is therefore the
native GitHub matrix and the existing `unittest` suite.

## Decision

| Tool or method | Decision | Reason |
|---|---|---|
| GitHub Actions OS and Python matrices | Use | GitHub matrices directly vary operating systems and language versions; hosted runners provide real isolated VMs. |
| `actions/setup-python` | Use, pinned | It resolves explicit interpreter versions; explicit versions avoid the runner's changing default Python. |
| Python `unittest`, `tempfile`, and `subprocess` | Use | They execute both installers end to end in isolated directories without another dependency. |
| Windows PowerShell 5.1, PowerShell 7, and Git Bash | Use on `windows-latest` | These are the actual supported Windows shells, so execution is stronger evidence than parsing or mocks. |
| tox or Nox | Do not add | Both manage multi-interpreter virtual environments, but this repository has no package or Python dependencies; the native matrix runs the same commands with less configuration. |
| Pester | Do not add | Pester is valuable for PowerShell unit/mocking work; this short installer is better covered by direct subprocess scenarios in both PowerShell editions. |
| ShellCheck and PSScriptAnalyzer | Do not add yet | Static analyzers are useful, but actual execution, strict shell mode, syntax parsing, and adversarial review cover the current scripts without a download or policy file. Add one only after a defect demonstrates a static-analysis gap. |
| Containers or local `act` emulation | Do not use as platform proof | A Linux container cannot reproduce hosted macOS or Windows shell behavior. |
| GUI automation | Do not add | Native Codex controls belong to the client; fixtures validate branching, while a real task supplies narrowly scoped manual UI evidence. |

## Maintained contract

- CPython 3.10 is the minimum because it is the oldest security-supported
  CPython listed by the cited Python status page. CI runs every supported minor
  through 3.14.
- The OS matrix uses GitHub's moving `-latest` labels to catch current hosted
  environment changes. Run logs record the actual Python and platform strings.
- Installer tests cover spaces, Unicode, collisions, idempotent upgrades,
  stale-file removal, unrelated-skill preservation, exact source parity, and
  all capability diagnostic branches.
- Codex has no numeric minimum in this project. A version is usable for the
  approval workflow only when the active surface exposes the required native
  tools; unsupported surfaces block safely.

## Primary sources

- [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills.md) documents
  `$HOME/.agents/skills`, automatic skill detection, and restart behavior.
- [OpenAI Codex configuration](https://learn.chatgpt.com/docs/config-file/config-basic.md)
  documents feature flags and configuration precedence.
- [GitHub matrix syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstrategymatrix)
  and [hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
  define the platform/version execution model.
- [`actions/setup-python`](https://github.com/actions/setup-python) recommends
  explicit versions instead of the runner's variable default.
- [Python version status](https://devguide.python.org/versions/) and
  [`unittest`](https://docs.python.org/3/library/unittest.html) define the
  supported interpreter range and standard test runner.
- [tox](https://tox.wiki/en/latest/), [Nox](https://nox.thea.codes/en/stable/),
  [Pester](https://pester.dev/docs/quick-start/),
  [PSScriptAnalyzer](https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/overview),
  and [ShellCheck](https://github.com/koalaman/shellcheck) were evaluated for
  the rejected alternatives above.
