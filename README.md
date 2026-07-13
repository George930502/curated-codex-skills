# Prompt Review and Dispatch

Codex skills that audit and polish GPT-5.6 prompts, clarify purpose through
native choices, require explicit approval, then queue the approved prompt into
the verified Codex task.

## Skills

- `prompt-master-gpt5` — audit or polish a GPT-5.6 prompt.
- `prompt-review-and-dispatch` — clarify, polish, approve, and dispatch.
- `grill-with-docs` — Matt Pocock's grilling/domain-modeling composition.
- `grilling` — one-decision-at-a-time interviewing with native Codex input.
- `domain-modeling` — maintain project language and durable decisions.

The authoritative native-input contract is
`skills/grilling/NATIVE-INPUT.md`. GPT-5.6 facts live only in
`skills/prompt-master-gpt5/references/openai-gpt56-prompting.md`.

Per the product contract, every incomplete prompt review invokes
`grill-with-docs`, not bare `grilling`. Its domain-modeling branch writes only
when an actual term is resolved or a candidate decision passes the ADR gate.

## Evidence

[`SOURCES.md`](SOURCES.md) pins every upstream commit, source path, hash, and
local adaptation. [`AUTHORING-AUDIT.md`](AUTHORING-AUDIT.md) records the invoked
skill standards and resulting checks. The repository is MIT licensed;
third-party notices are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Install

Clone the repository, enter it, then run the installer for your shell. The
installers copy every skill into the
[official user-level directory](https://learn.chatgpt.com/docs/build-skills.md#where-to-save-skills),
`$HOME/.agents/skills`, without requiring `rsync`. On Windows this resolves to
`%USERPROFILE%\.agents\skills`.

### macOS/Linux, WSL, or Git Bash

```bash
git clone https://github.com/George930502/prompt-review-and-dispatch.git
cd prompt-review-and-dispatch
bash scripts/install.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/George930502/prompt-review-and-dispatch.git
Set-Location .\prompt-review-and-dispatch
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

### Enable native input on Windows

The workflow requires Codex's native `request_user_input` control. In
PowerShell, verify and persistently enable it before starting a new Codex task:

```powershell
codex features list | Select-String "default_mode_request_user_input"
codex features enable default_mode_request_user_input
codex features list | Select-String "default_mode_request_user_input"
```

The final line must end in `true`. Fully close Codex, start a new session, then
invoke `$prompt-review-and-dispatch`. If the feature remains `false` or is not
listed, see [Windows native-input troubleshooting](docs/windows-native-input.md).

The final invocation must run inside a configured and authenticated Codex
session. Installing the skills does not provide Codex credentials; an
isolated `codex exec` without authentication will return `401 Unauthorized`.

## Validate

The validator uses the current Python interpreter and forces UTF-8 mode, so it
does not depend on the Windows system code page. Install its `PyYAML`
dependency once before running it.

### macOS/Linux, WSL, or Git Bash

```bash
python3 -m pip install -r scripts/requirements-validation.txt
python3 scripts/validate.py
```

### Windows PowerShell

```powershell
py -3 -m pip install -r .\scripts\requirements-validation.txt
py -3 .\scripts\validate.py
```

The command validates the installed copy in `$HOME/.agents/skills`. It uses the
Codex system validator at
`${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py`.
To validate the checkout before installing, append `--skills-dir skills`.

Codex still recognizes skills installed by its bundled installer under
`$CODEX_HOME/skills`, but this repository uses the current documented global
authoring location to avoid platform-specific destinations. Remove older copies
of these same five skills from `$CODEX_HOME/skills` after verifying the new
installation, otherwise duplicate names can appear in the skill selector.
