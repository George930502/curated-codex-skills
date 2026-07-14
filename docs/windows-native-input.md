# Windows native-input prerequisite

`prompt-review-and-dispatch` requires the host-native `request_user_input`
control for every clarification, alignment, rejection, and approval decision.
It intentionally blocks instead of substituting a prose question.

## Confirmed failure

On Windows, a newly installed Codex session can report:

```text
Coverage: incomplete
Gate: needs-purpose-clarification
native request_user_input unavailable
```

The skill is installed correctly when it reaches this audit. The failure means
the host did not register the native input tool for that Default session.

When the tool is available, an empty return is not an approval and has no retry
limit. The skill must immediately reissue the same native control while the task
remains active; it must not fall back to a prose question after three attempts.

The confirmed configuration signal is:

```powershell
codex features list | Select-String "default_mode_request_user_input"
```

```text
default_mode_request_user_input  under development  false
```

This capability is intentionally detected by name and effective state rather
than by a guessed minimum Codex version. A Linux Codex desktop task directly
observed it as enabled with `codex-cli 0.144.1` on 2026-07-14; that is not
Windows client evidence. The feature remains marked `under development`, so
every Windows client must pass the capability check directly.

## Enable it from PowerShell

Persistently enable the feature through Codex itself:

```powershell
codex features enable default_mode_request_user_input
```

Verify the effective state:

```powershell
codex features list | Select-String "default_mode_request_user_input"
```

The line must end in `true`. Then fully close the Codex CLI or Windows app and
start a new task. Tool availability is established when a task starts; resuming
the already blocked task may preserve its old tool set.

Codex stores the persistent setting under
`%USERPROFILE%\.codex\config.toml`. Prefer `codex features enable` over editing
TOML manually because it preserves existing configuration structure.

To undo the opt-in:

```powershell
codex features disable default_mode_request_user_input
```

## If it is absent or remains false

1. Update Codex and check its version:

   ```powershell
   codex update
   codex --version
   codex features list | Select-String "default_mode_request_user_input"
   ```

2. If using the Microsoft Store Windows app, update the app, fully exit it, and
   start a new task. The CLI in an integrated terminal and the app runtime can
   have different versions.
3. Use an interactive Codex task. Non-interactive `codex exec`, review agents,
   cloud tasks, and other restricted surfaces may not expose native questions.
4. Run `/plan` as a diagnostic. If native questions work there but not in
   Default mode, the Default-mode feature is still not effective.
5. Collect these results when reporting the problem:

   ```powershell
   codex --version
   codex features list
   codex doctor
   ```

Do not publish `config.toml` without removing tokens, private MCP settings, and
machine-specific paths.

## Why the installer does not enable it automatically

`default_mode_request_user_input` is currently marked `under development` by
Codex. The installers detect and explain the missing prerequisite, but do not
silently mutate a user's global Codex feature configuration. The explicit
`codex features enable` command records that opt-in.

Fixing this capability enables the clarification and approval gates. Final
dispatch additionally requires the active Codex surface to expose its task
lookup and message-send tools; the skill will remain blocked rather than claim
success if those tools are unavailable.
